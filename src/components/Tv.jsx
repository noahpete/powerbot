import React from "react";
import ReactPlayer from "react-player";

const Tv = ({ yt_id, start_time_s }) => {
  return (
    <div className="">
      <ReactPlayer
        url={`https://www.youtube.com/watch?v=${yt_id}&t=${start_time_s}`}
        width={370}
        height={208}
        controls={true}
        playing
      />
    </div>
  );
};

export default Tv;
