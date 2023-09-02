import { createTheme } from "@mui/material";

export const THEME = createTheme({
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

// General
export const COLUMN_WIDTH = 400;
export const MAX_SINGLE_COL_WIDTH = 640;
export const COMPONENT_MT = "mt-2";

// App.jsx
export const ADVANCE_SONG_FETCH_MS = -12000;
export const MAX_SETLIST_LENGTH = 60;

// Searchbar.jsx
export const SEARCHBAR_REFRESH_MS = 500;

// SongCard.jsx
export const MAX_ARTISTS_SHOWN = 3;
