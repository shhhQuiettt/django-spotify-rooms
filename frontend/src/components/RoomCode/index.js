import React from "react";
import PropTypes from "prop-types";
import "./index.css";

const RoomCode = ({ code }) => {
  return (
    <div className="room-code">
      <h2>Room code:</h2>

      <div className="inside-shadow">
        <h1>{code}</h1>
      </div>
    </div>
  );
};

RoomCode.propTypes = {
  code: PropTypes.string.isRequired,
};
export default RoomCode;
