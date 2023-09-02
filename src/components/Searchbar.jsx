import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import * as constants from "../constants";
import SearchIcon from "@mui/icons-material/Search";
import SongCard from "./SongCard";

const Searchbar = ({ songCardAddFunc, children }) => {
  const [songList, setSongList] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const timeoutRef = useRef(null);
  const inputRef = useRef(null);

  const fetchData = async (term) => {
    if (!term || term.trim() === "") {
      setSongList(null);
      return;
    }
    axios
      .get(`api/songs/search/${term}/`)
      .then(async (res) => {
        const data = await res.data;
        console.log("data", data.items);
        setSongList(data.items);
        return data.items;
      })
      .catch((err) => {
        // setIsPlaing(false) ?
        console.error(err);
      });
  };

  const handleInputChange = (e) => {
    const term = e.target.value;
    setSearchTerm(term.split(".").join(" "));

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(async () => {
      const data = await fetchData(term);
      if (data) {
        setSongList(data["items"]);
      }
      setIsExpanded(term.trim());
      if (!term) setSongList(null);
    }, constants.SEARCHBAR_REFRESH_MS);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!searchTerm) {
      return;
    }
  };

  useEffect(() => {
    // Event listener to handle clicks outside the input element
    const handleClickOutside = (event) => {
      if (
        !songList &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setIsExpanded(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      // cleanup
      document.removeEventListener("mousedown", handleClickOutside);
      clearTimeout(timeoutRef.current);
    };
  }, [isExpanded, songList]);

  return (
    <form className="flex w-full" onSubmit={(e) => handleSubmit(e)}>
      <div id="searchbar-container" className=" w-full">
        <div
          id="searchbar"
          className={`${constants.COMPONENT_MT} bg-white flex shadow-sm p-1 outline outline-1 outline-gray-200 h-8`}
        >
          <SearchIcon className="text-gray-400 ml-2" />
          <input
            placeholder="Search for tracks, artists, albums..."
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={() => setIsExpanded(true)}
            className="bg-transparent w-full ml-2 outline-none border-none text-md"
          />
        </div>

        <div
          id="songs"
          className={`${constants.COMPONENT_MT} w-full opacity-${
            isExpanded ? "100" : "0"
          } outline outline-[#E5E7EB] outline-1`}
        >
          {songList?.map((song, i) => (
            <SongCard
              songData={song}
              small={true}
              addFunction={songCardAddFunc}
              key={i}
            />
          ))}
        </div>
      </div>
    </form>
  );
};

export default Searchbar;
