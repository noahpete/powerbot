import React, { useEffect, useState } from "react";
import axios from "axios";
import SongCard from "./components/SongCard";
import Searchbar from "./components/Searchbar";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { Button, LinearProgress } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import Logo from "./assets/powerbotlogo.png";

const theme = createTheme({
  palette: {
    primary: {
      main: "#ffffff",
    },
    secondary: {
      main: "#94a3b8",
    },
    blue: {
      main: "#00B0E9",
      contrastText: "#fff",
    },
    red: {
      main: "#EA0101",
      contrastText: "#fff",
    },
    yellow: {
      main: "#F5B11B",
      contrastText: "#fff",
    },
  },
  typography: {
    fontFamily: ['"Segoe UI"', "Helvetica", "Arial", "Roboto"].join(","),
  },
});

function uuid4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0,
      v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

const Main = () => {
  const [songIds, setSongIds] = useState([]);
  const [songs, setSongs] = useState([]);
  const [downloadReady, setDownloadReady] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [sessionId, setSessionId] = useState("");

  const addSong = (song) => {
    const newSongs = [...songs];
    newSongs.push(song);
    setSongs(newSongs);
  };

  const removeSong = (songId) => {
    const newSongs = [...songs];
    const idxToRemove = songs.findIndex((song) => song.id === songId);
    if (idxToRemove !== -1) {
      newSongs.splice(idxToRemove, 1);
    }
    setSongs(newSongs);
  };

  const handleGenerate = () => {
    if (songs.length < 1) {
      return;
    }
    if (sessionId) {
      handleClear();
    }
    const newId = uuid4();
    setSessionId(newId);
    setIsGenerating(true);
    setDownloadReady(false);
    axios
      .post("/api/bot/generate/", {
        songs: songs,
        sessionId: newId,
      })
      .then((response) => {
        setIsGenerating(false);
        setDownloadReady(true);
      })
      .catch((err) => {
        setIsGenerating(false);
        console.log(err);
      });
  };

  const handleDownload = () => {
    const config = {
      method: "GET",
      url: "/api/bot/download/",
      responseType: "blob",
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
      params: {
        sessionId: sessionId,
      },
    };

    axios(config).then((response) => {
      const link = document.createElement("a");
      link.target = "_blank";
      link.download = "output.mp4";
      link.href = URL.createObjectURL(
        new Blob([response.data], { type: "video/mp4" })
      );
      link.click();
    });
  };

  const handleShuffle = () => {
    const newSongs = [...songs];
    for (let i = newSongs.length - 1; i > 0; i--) {
      let j = Math.floor(Math.random() * (i + 1));
      let temp = newSongs[i];
      newSongs[i] = newSongs[j];
      newSongs[j] = temp;
    }
    console.log(newSongs);
    setSongs(newSongs);
  };

  const handleClear = () => {
    axios.post("/api/bot/clear/", sessionId);
  };

  const setupBeforeUnloadListener = () => {
    window.addEventListener("beforeunload", (event) => {
      event.preventDefault();
      handleClear();
    });
  };

  useEffect(() => {
    setupBeforeUnloadListener();
  });

  return (
    <ThemeProvider theme={theme}>
      <div className="bg-white flex relative w-100vh">
        <div className="flex">
          <div className="w-[400px] mr-4 mt-10 p-4 top-10"></div>
          <div className="w-[400px] h-0 mr-4 p-4 justify-center fixed top-10">
            <img className="ml-4 mb-4" src={Logo} alt="" />

            <Searchbar
              songIds={songIds}
              setSongIds={setSongIds}
              addFunction={addSong}
            />
            <div className="w-[400px] mt-3 flex justify-center">
              <Button
                className="m-1"
                color="secondary"
                variant={
                  !isGenerating && songs.length > 1 ? "outlined" : "outlined"
                }
                onClick={handleShuffle}
              >
                Shuffle
              </Button>
              <Button
                className="m-1"
                onClick={handleGenerate}
                color="red"
                variant={
                  isGenerating || songs.length === 0 ? "contained" : "contained"
                }
              >
                Generate
              </Button>
              <Button
                className="m-1"
                onClick={handleDownload}
                color="blue"
                variant={downloadReady ? "contained" : "disabled"}
              >
                Download
              </Button>
            </div>
            <div className="">
              {isGenerating ? (
                <>
                  <LinearProgress
                    color="blue"
                    className="h-[4px] w-[300px] ml-[12.5%]"
                  />
                </>
              ) : (
                ""
              )}
            </div>
          </div>
          <div className="flex p-4 right-10 justify-center h-0 mt-10">
            <div className="w-[410px] h-fit shadow-sm flex flex-col gap-0 outline outline-1 outline-gray-200 p-1.5">
              {songs.length === 0 ? (
                <p className="ml-2 text-gray-400 text-center">
                  Got some work to do...
                </p>
              ) : (
                ""
              )}
              <DragDropContext
                onDragEnd={(res) => {
                  if (!res.destination) return;
                  const items = Array.from(songs);
                  const [reorderedItem] = items.splice(res.source.index, 1);
                  items.splice(res.destination.index, 0, reorderedItem);
                  setSongs(items);
                }}
              >
                <Droppable droppableId="songs">
                  {(provided) => (
                    <ul
                      className="songs divide-y divide-gray-200"
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                    >
                      {songs.map((song, i) => (
                        <Draggable
                          key={`${song.id}${i}`}
                          draggableId={`${song.id}${i}`}
                          index={i}
                        >
                          {(provided) => (
                            <li
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              ref={provided.innerRef}
                            >
                              <SongCard
                                song={song}
                                i={i}
                                removeFunction={removeSong}
                              />
                            </li>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </ul>
                  )}
                </Droppable>
              </DragDropContext>
            </div>
          </div>
        </div>
      </div>
    </ThemeProvider>
  );
};

export default Main;
