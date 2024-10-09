import React from "react";
import "./icon.css";

class Icon extends React.Component {
  render() {
    return (
      <>
        <div className="icon">
          <img className="logo" src="img/so_logo.png" alt="logo" />
          Stack Overflow
        </div>
        <br />
      </>
    );
  }
}

export default Icon;
