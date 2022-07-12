import React from "react";
import "./index.css";
import { Link } from "react-router-dom";

const NavButtons = () => {
  return (
    <div className="nav-buttons">
      <Link to={"/room/join"}>
        <button className="join-button">Join a room</button>
      </Link>
      <Link to={"/room/create"}>
        <button className="create-button">Create a room</button>
      </Link>
    </div>
  );
};

export default NavButtons;
