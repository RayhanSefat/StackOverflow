import React from "react";
import "./icon.css";

class Icon extends React.Component {
  render() {
    return (
      <>
        <div class="icon">
          <img class="logo" src="img/so_logo.png" alt="logo" />
          Stack Overflow
        </div>
        <br />
      </>
    );
  }
}

export default Icon;
