import React from "react";
import { LinearProgress } from "@mui/material";
import * as constants from "../constants.js";

const Controls = ({ children, isLoading = false }) => {
  return (
    <div id="controls">
      <div id="loading-bar" className="h-[8px]">
        {isLoading ? (
          <LinearProgress
            sx={{
              height: 8,
            }}
          ></LinearProgress>
        ) : (
          ""
        )}
      </div>

      <div id="buttons-count" className="flex">
        {children}
      </div>
    </div>
  );
};

export default Controls;
