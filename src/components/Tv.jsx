import React, { useEffect } from "react";
import ReactPlayer from "react-player";
import * as constants from "../constants";

const Tv = ({ youtubeId, startTimeS, playing = true }) => {
  useEffect(() => {
    console.log(
      `link: https://www.youtube.com/watch?v=${youtubeId}&t=${startTimeS}`
    );
  }, [youtubeId]);

  return (
    <div id="tv-container" className="w-full aspect-video">
      <ReactPlayer
        url={`https://www.youtube.com/watch?v=${youtubeId}&t=${startTimeS}`}
        width={"100%"}
        height={"100%"}
        controls
        playing={playing}
      />
    </div>
  );
};

export default Tv;
