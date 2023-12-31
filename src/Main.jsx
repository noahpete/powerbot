import React, { useEffect, useState } from "react";
import axios from "axios";
import SongCard from "./components/SongCard";
import Searchbar from "./components/Searchbar";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { Button, LinearProgress } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import Logo from "./assets/powerbotlogo.png";
import ReactPlayer from "react-player";

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
      main: "#C01B22",
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
  const [songsReady, setSongsReady] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isTelevising, setIsTelevising] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [songData, setSongData] = useState([]);
  const [curYtId, setCurYtId] = useState("");
  const [curStartTimeMs, setCurStartTimeMs] = useState(null);
  const [isLastSong, setIsLastSong] = useState(false);

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

  const televise = () => {
    let curDelayMs = 0;
    console.log("televising...");
    setCurYtId("");
    setIsTelevising(true);
    setIsLastSong(false);
    songData.forEach((song, index) => {
      const chorus_length_ms = song.chorus_time_ms[1] - song.chorus_time_ms[0];
      console.log(
        `Playing ${song.title} by ${song.artist} for ${
          chorus_length_ms / 1000
        } seconds.`
      );
      setTimeout(() => {
        // if (isTelevising) {
        console.log(index, song);
        setCurYtId(song.yt_id);
        setCurStartTimeMs(song.chorus_time_ms[0]);
        // }
      }, curDelayMs);
      curDelayMs += chorus_length_ms;
    });
    setTimeout(() => {
      setIsTelevising(false);
      setIsLastSong(true);
    }, curDelayMs + 1000);
  };

  const handleGenerate = () => {
    if (songs.length < 1 || isGenerating) {
      return;
    }
    if (sessionId) {
      handleClear();
    }
    const newId = uuid4();
    setSessionId(newId);
    setIsGenerating(true);
    setIsTelevising(false);
    setIsLastSong(false);
    setSongsReady(false);
    axios
      .post("/api/bot/generate/", {
        songs: songs,
        sessionId: newId,
      })
      .then((response) => {
        setIsGenerating(false);
        console.log("response", response.data);
        setSongData(response.data);
        console.log("songdata:", response.data);
        setSongsReady(true);
      })
      .catch((err) => {
        setIsGenerating(false);
        console.log(err);
      });
  };

  const handleDownload = () => {
    if (isGenerating) {
      return;
    }
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

  const fetchVideo = ({ videoUrl }) => {
    // const options = {
    //   headers: {
    //     Authorization: `Bearer ${token}`,
    //   },
    // };
    // const [url, setUrl] = useState();
    // useEffect(() => {
    //   fetch(videoUrl, options)
    //     .then((response) => response.blob())
    //     .then((blob) => {
    //       setUrl(URL.createObjectURL(blob));
    //     });
    // }, [videoUrl]);
  };

  useEffect(() => {
    setupBeforeUnloadListener();
  });

  return (
    <ThemeProvider theme={theme}>
      <div className="w-full h-full p-4">
        <div id="container" className="md:flex max-w-[854px] w-full m-auto">
          <div id="control" className="max-w-sm m-auto">
            <div id="logo" className="">
              <img src={Logo} className="" alt="logo" />
            </div>
            <div id="searchbar-and-buttons" className="w-full mt-4">
              <div className="">
                {isGenerating ? (
                  <>
                    <LinearProgress color="blue" className="h-[4px] w-full" />
                  </>
                ) : (
                  <div className="h-[4px]"></div>
                )}
              </div>

              <div id="buttons" className="flex justify-center mb-2">
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
                    isGenerating || songs.length === 0
                      ? "contained"
                      : "contained"
                  }
                >
                  Generate
                </Button>
                <Button
                  className="m-1"
                  onClick={televise}
                  color="blue"
                  variant={
                    songsReady && !isTelevising ? "contained" : "disabled"
                  }
                >
                  {isTelevising ? "No stopping now..." : "Start"}
                </Button>
              </div>

              <Searchbar
                songIds={songIds}
                setSongIds={setSongIds}
                addFunction={addSong}
              />
            </div>
          </div>

          <div className="w-full ml-auto mr-auto max-w-sm p-2 mt-2">
            <div id="tv-container" className="w-full h-[210px]">
              <ReactPlayer
                url={`https://www.youtube.com/watch?v=${curYtId}&t=${
                  curStartTimeMs / 1000
                }`}
                width={370}
                height={208}
                controls={true}
                playing={isTelevising || isLastSong}
              />
            </div>

            <div
              id="songcards"
              className="w-full ml-auto mr-auto max-w-sm p-2 mt-2 h-fit shadow-sm flex flex-col gap-0 outline outline-1 outline-gray-200"
            >
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
