import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import SearchIcon from "@mui/icons-material/Search";
import SongCard from "./SongCard";

const Searchbar = ({ addFunction, isGray }) => {
  const INPUT_REFRESH_MS = 500;

  const [list, setList] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);
  const debounceTimeoutRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Event listener to handle clicks outside the input element
    const handleClickOutside = (event) => {
      if (
        !list &&
        inputRef.current &&
        !inputRef.current.contains(event.target)
      ) {
        setIsExpanded(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      clearTimeout(debounceTimeoutRef.current);
    };
  }, [isExpanded, list]);

  const fetchData = async (term) => {
    if (!term || term.trim() === "") {
      setList(null);
      return;
    }
    axios
      .get(`api/songs/search/${term}/`)
      .then(async (res) => {
        const data = await res.data;
        setList(data.items);
        return data.items;
      })
      .catch((err) => {
        console.error(err);
      });
  };

  const handleInputChange = (event) => {
    const term = event.target.value;
    setSearchTerm(term.split(".").join(" "));

    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    debounceTimeoutRef.current = setTimeout(async () => {
      const data = await fetchData(term);
      if (data !== null) {
        setList(data);
      }
      // Set isExpanded to false only if the searchTerm is empty
      setIsExpanded(term.trim());
      if (!searchTerm) setList(null);
    }, INPUT_REFRESH_MS);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!searchTerm) {
      return;
    }
  };

  return (
    <form onSubmit={(event) => handleSubmit(event)} autoComplete="off">
      <div className="bg-white flex shadow-sm p-1 outline outline-1 outline-gray-200 w-full h-8">
        <SearchIcon className="text-gray-400 ml-2" />
        <input
          ref={inputRef} // Add a reference to the input element
          className="bg-transparent w-full ml-2 outline-none border-none text-md"
          name="search-field"
          autoComplete="off"
          id="search-field"
          placeholder="Search for tracks, artists, albums..."
          type="search"
          value={searchTerm}
          onChange={handleInputChange}
          onFocus={() => setIsExpanded(true)}
        />
      </div>
      <div
        className={`mt-2 full outline outline-1 outline-gray-200 transition-height duration-500 ease-in-out h-8 ${
          isExpanded ? "h-fit" : "h-0"
        }`}
      >
        {list?.map((song, i) => (
          <SongCard
            song={song}
            small={true}
            addFunction={addFunction}
            key={i}
            isGray={isGray}
          />
        ))}
      </div>
    </form>
  );
};

export default Searchbar;
