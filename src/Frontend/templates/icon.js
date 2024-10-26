import React from "react";
import { useNavigate } from "react-router-dom";
import "./icon.css";

function Icon() {
  const navigate = useNavigate();

  return (
    <>
      <div className="icon">
        <img className="logo" src="img/so_logo.png" alt="" />
        <span className="stack-link" onClick={() => navigate("/")}>
          Stack Overflow
        </span>
      </div>
      <br />
    </>
  );
}

export default Icon;
