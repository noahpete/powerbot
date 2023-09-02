import React from "react";
import { IconButton } from "@mui/material";
import { Add, Remove } from "@mui/icons-material";
import * as constants from "../constants";

const SongCard = ({
  songData,
  small = false,
  addFunction,
  removeFunction,
  index,
}) => {
  const dimensions = small ? "h-12 w-12" : "h-20 w-20";

  const handleAddSong = () => {
    addFunction(songData);
  };

  const handleRemoveSong = () => {
    removeFunction(index);
  };

  return (
    <div className="flex w-full p-0.5 transition ease-in hover:bg-gray-100">
      <div id="album-art" className="flex-shrink-0">
        <img
          src={songData?.album.images[1]?.url}
          className={`object-cover ${dimensions}`}
          alt="album cover"
        />
      </div>

      <div
        id="song-info"
        className="ml-4 flex-grow flex flex-col justify-center overflow-hidden"
      >
        <h1
          className={`font-bold ${
            small ? "text-sm leading-none" : "text-lg"
          } truncate`}
        >
          {songData.name}
        </h1>
        <p className={`font-light ${small ? "text-xs" : "text-sm"} truncate`}>
          {songData.artists.map(
            (artist, i) =>
              `${
                i < constants.MAX_ARTISTS_SHOWN
                  ? `${artist.name}${
                      i === songData.artists.length - 1 || i === 2 ? "" : ","
                    } `
                  : ""
              }`
          )}
        </p>
      </div>

      <div id="card-func" className="aspect-square">
        <IconButton onClick={small ? handleAddSong : handleRemoveSong}>
          {small ? (
            <Add className="text-gray-400 mt-[2px]" />
          ) : (
            <Remove className="text-gray-400" />
          )}
        </IconButton>
      </div>
    </div>
  );
};

export default SongCard;
