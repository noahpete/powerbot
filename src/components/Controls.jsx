import React from "react";
import { LinearProgress } from "@mui/material";
import * as constants from "../constants.js";

const Controls = ({ children, isLoading = false }) => {
  return (
    <div id="controls" className="bg-white">
      <div id="buttons-count" className="flex">
        {children}
      </div>
    </div>
  );
};

export default Controls;
