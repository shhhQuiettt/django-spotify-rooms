import React from "react";
import "./index.css";
import GoBackButton from "../GoBackButton";
import { BsSpotify } from "react-icons/bs";

const Header = () => {
  return (
    <header>
      <GoBackButton />
      <h1>Spotify room app</h1>
      <BsSpotify fontSize={34} />
    </header>
  );
};

export default Header;
