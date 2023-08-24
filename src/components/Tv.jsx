import React from "react";
import ReactPlayer from "react-player";

const Tv = ({ yt_id }) => {
  return (
    <div className="">
      <ReactPlayer
        url={"https://www.youtube.com/watch?v=QtTR-_Klcq8"}
        width={370}
        height={208}
        playing={true}
        controls={true}
      />
    </div>
  );
};

export default Tv;
