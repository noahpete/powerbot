import React, { useState, useEffect, useRef } from "react";
import SearchIcon from "@mui/icons-material/Search";
import SongCard from "./SongCard";

const Searchbar = ({ addFunction }) => {
  const INPUT_REFRESH_MS = 500;

  const [list, setList] = useState(null);
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
      // Cleanup function to remove the event listener when the component unmounts
      document.removeEventListener("mousedown", handleClickOutside);
      // Cleanup function to clear the debounceTimeout when the component unmounts
      clearTimeout(debounceTimeoutRef.current);
    };
  }, [isExpanded, list]);

  const fetchData = async (searchTerm) => {
    if (!searchTerm || searchTerm.trim() === "" || searchTerm === "") {
      setList(null);
      return;
    }
    try {
      const response = await fetch(
        `http://powerbot-1f0600cd4beb.herokuapp.com/api/songs/search/${searchTerm}/`
      );
      // console.log(response);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching data:", error);
      return null;
    }
  };

  const handleInputChange = (event) => {
    const term = event.target.value;
    setSearchTerm(term);

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
      <div className="bg-white flex shadow-sm p-1 outline outline-1 outline-gray-200 w-[400px] h-8">
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
        className={`mt-2 w-[400px] outline outline-1 outline-gray-200 transition-height duration-500 ease-in-out h-8 ${
          isExpanded ? "h-[520px]" : "h-0"
        }`}
      >
        {list?.tracks.items.map((item, i) => (
          <SongCard
            addFunction={addFunction}
            key={i}
            song={item}
            i={i}
            small={true}
          />
        ))}
      </div>
    </form>
  );
};

export default Searchbar;
