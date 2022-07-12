import React from "react";
import { FaArrowLeft } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import "./index.css";

const GoBackButton = () => {
  let navigate = useNavigate();
  return (
    <button className="go-back-button" onClick={() => navigate(-1)}>
      {/* <BiArrowBack /> */}
      <FaArrowLeft />
    </button>
  );
};

export default GoBackButton;
