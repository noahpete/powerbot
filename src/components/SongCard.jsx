import React from "react";
import IconButton from "@mui/material/IconButton";
import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";

const MAX_ARTISTS_SHOWN = 10;

const SongCard = ({ song, small = false, addFunction, removeFunction }) => {
  const handleAddSong = () => {
    addFunction(song);
  };

  const handleRemoveSong = () => {
    removeFunction(song.id);
  };

  return (
    <div
      draggable="true"
      className="flex w-full p-0.5 transition ease-in hover:bg-gray-100"
    >
      <div className={` w-${small ? "12" : "20"} h-${small ? "12" : "20"}`}>
        <img
          alt="song album cover"
          src={song?.album.images[1]?.url}
          className="h-full w-full"
        />
      </div>
      <div
        className={`flex flex-col justify-center ${
          small ? "h-12" : "h-20"
        } w-[140px] ml-4`}
      >
        <h1
          className={`font-bold ${
            small ? "text-sm leading-none" : "text-lg"
          } truncate`}
        >
          {song.name}
        </h1>
        <p className={`font-light ${small ? "text-xs" : "text-sm"} truncate`}>
          {song.artists.map(
            (artist, i) =>
              `${
                i < MAX_ARTISTS_SHOWN
                  ? `${artist.name}${
                      i === song.artists.length - 1 || i === 2 ? "" : ","
                    } `
                  : ""
              }`
          )}
        </p>
      </div>
      {small ? (
        <div className="aspect-square ml-[80px] mt-1">
          <IconButton onClick={handleAddSong}>
            <AddIcon className="text-gray-400"></AddIcon>
          </IconButton>
        </div>
      ) : (
        <div className="aspect-square ml-[45px] mt-[18px]">
          <IconButton onClick={handleRemoveSong}>
            <RemoveIcon className="text-gray-400"></RemoveIcon>
          </IconButton>
        </div>
      )}
    </div>
  );
};

export default SongCard;
