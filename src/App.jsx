import React, { useState, useEffect } from "react";
import axios from "axios";
import { IconButton, LinearProgress } from "@mui/material";
import { ThemeProvider } from "@mui/material/styles";
import ShuffleIcon from "@mui/icons-material/Shuffle";
import RepeatIcon from "@mui/icons-material/RestartAlt";
import PlayIcon from "@mui/icons-material/PlayArrow";
import StopIcon from "@mui/icons-material/Stop";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { Controls, Searchbar, SongCard } from "./components";
import * as constants from "./constants";
import logo from "./assets/powerbotlogo.png";
import Tv from "./components/Tv";

const App = () => {
  const [screenSize, setScreenSize] = useState(window.innerWidth);
  const [setlist, setSetlist] = useState([]);
  const [curYoutubeId, setCurYoutubeId] = useState("");
  const [curStartMs, setCurStartMs] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [timeoutId, setTimeoutId] = useState(null);
  const [curIndex, setCurIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isGray, setIsGray] = useState(false);

  const addToSetlist = (song) => {
    setCurIndex(0);
    if (setlist.length >= constants.MAX_SETLIST_LENGTH) return;
    const newSetlist = [...setlist];
    newSetlist.push(song);
    setSetlist(newSetlist);
  };

  const removeFromSetlist = (songIndex) => {
    setCurIndex(0);
    const newSetlist = [...setlist];
    newSetlist.splice(songIndex, 1);
    setSetlist(newSetlist);
  };

  const handleShuffle = () => {
    setCurIndex(0);
    const newSetlist = [...setlist];
    for (let i = newSetlist.length - 1; i > 0; i--) {
      let j = Math.floor(Math.random() * (i + 1));
      let temp = newSetlist[i];
      newSetlist[i] = newSetlist[j];
      newSetlist[j] = temp;
    }
    setSetlist(newSetlist);
  };

  const handlePlay = async (usedIndex) => {
    if (setlist.length < 1) return;

    setCurYoutubeId("");

    let curDelayMs = 0;
    for (const [index, song] of setlist.entries()) {
      if (index < usedIndex) {
        continue;
      }
      await new Promise((res) => {
        const newTimeoutId = setTimeout(
          res,
          curDelayMs + constants.ADVANCE_SONG_FETCH_MS
        );
        setTimeoutId(newTimeoutId);
      });

      try {
        setIsLoading(true);
        setIsPlaying(true);
        const response = await axios.get(`/api/songs/${song.id}/`);
        if (response.data.status == "success") {
          setIsGray(true);
          setIsLoading(false);
          setCurIndex(index);
          setCurYoutubeId(response.data.youtube_id);
          setCurStartMs(response.data.start_time_ms);
        } else {
          // TODO: give error flag for song in setlist
        }
        curDelayMs = response.data.duration_ms;
      } catch (error) {
        console.error("Error fetching song data:", error);
      }
    }
  };

  const handleRestart = () => {
    const newIndex = 0;
    setCurIndex(newIndex);
    handlePlay(newIndex);
  };

  const handleStop = () => {
    setIsPlaying(false);
    setIsGray(false);
    if (timeoutId !== null) {
      setIsLoading(false);
      clearTimeout(timeoutId);
      setTimeoutId(null);
    }
  };

  const handleResize = () => {
    setScreenSize(window.innerWidth);
  };

  useEffect(() => {
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <ThemeProvider theme={constants.THEME}>
      <div
        id="App"
        className={`w-full h-full p-4 ${isPlaying ? "bg-white" : "bg-white"}`}
      >
        <div
          id="main-container"
          className="sm:flex max-w-[854px] w-full m-auto"
        >
          <div
            id="left-col"
            className={`p-2 ${
              screenSize < constants.MAX_SINGLE_COL_WIDTH ? "w-full" : "w-1/2"
            }`}
          >
            <img src={logo} alt="logo" />
            <div id="tv" className={constants.COMPONENT_MT}>
              {screenSize < constants.MAX_SINGLE_COL_WIDTH ? (
                <Tv
                  youtubeId={curYoutubeId}
                  startTimeS={Math.floor(curStartMs / 1000)}
                  playing={isPlaying}
                />
              ) : (
                ""
              )}
            </div>
            {isLoading ? (
              <LinearProgress
                color="blue"
                sx={{
                  height: 8,
                }}
              ></LinearProgress>
            ) : (
              <div className="h-[8px]" />
            )}

            <Controls>
              <IconButton
                color="secondary"
                disabled={setlist.length < 2 || isPlaying}
                onClick={handleShuffle}
              >
                <ShuffleIcon />
              </IconButton>
              <IconButton
                color="yellow"
                disabled={setlist.length < 1 || isPlaying || isLoading}
                onClick={handleRestart}
              >
                <RepeatIcon />
              </IconButton>
              <IconButton
                color="blue"
                disabled={setlist.length < 1 || isPlaying || isLoading}
                onClick={() => handlePlay(curIndex)}
              >
                <PlayIcon />
              </IconButton>
              <IconButton
                color="red"
                disabled={!isPlaying && !isLoading}
                onClick={handleStop}
              >
                <StopIcon />
              </IconButton>
              {isPlaying || isLoading ? (
                <p id="stat" className={`${constants.COMPONENT_MT} m-auto`}>
                  track {curIndex + 1} / {setlist.length}
                </p>
              ) : (
                <p id="stat" className={`${constants.COMPONENT_MT} m-auto`}>
                  # tracks: {setlist.length} / {constants.MAX_SETLIST_LENGTH}
                </p>
              )}
            </Controls>
            <div
              className={
                isPlaying || isLoading
                  ? "pointer-events-none opacity-40 mt-2 transition ease-in-out duration-1000"
                  : "mt-2 transition ease-in-out duration-1000 "
              }
            >
              <Searchbar addFunction={addToSetlist} isGray={isGray} />
            </div>
          </div>

          <div
            id="right-col"
            className={
              screenSize < constants.MAX_SINGLE_COL_WIDTH
                ? "m-auto w-[97%]"
                : "w-1/2"
            }
          >
            {screenSize < constants.MAX_SINGLE_COL_WIDTH ? (
              ""
            ) : (
              <Tv
                youtubeId={curYoutubeId}
                startTimeS={Math.floor(curStartMs / 1000)}
                playing={isPlaying}
              />
            )}
            <div
              id="setlist"
              className={
                isPlaying || isLoading
                  ? "pointer-events-none opacity-40 mt-2"
                  : "mt-2"
              }
            >
              <DragDropContext
                onDragEnd={(dropResult) => {
                  setCurIndex(0);
                  if (!dropResult.destination) return;
                  const newSetlist = [...setlist];
                  const [reorderedSetlist] = newSetlist.splice(
                    dropResult.source.index,
                    1
                  );
                  newSetlist.splice(
                    dropResult.destination.index,
                    0,
                    reorderedSetlist
                  );
                  setSetlist(newSetlist);
                }}
              >
                <Droppable droppableId="setlist">
                  {(provided) => (
                    <ul
                      className={`setlist divide-y divide-gray-200 outline outline-gray-200 outline-1 ${
                        setlist.length > 0 ? "" : "opacity-0"
                      }`}
                      {...provided.droppableProps}
                      ref={provided.innerRef}
                    >
                      {setlist.map((song, i) => (
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
                                removeFunction={removeFromSetlist}
                                index={i}
                                isGray={isGray}
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

export default App;
