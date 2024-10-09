import React, { useEffect, useState } from "react";
import { Helmet } from "react-helmet";
import Icon from "../../templates/icon"; // Adjust the import path as necessary
import { Link } from "react-router-dom";

const Home = () => {
  const [message, setMessage] = useState("");

  const token = localStorage.getItem("token");

  const fetchData = async () => {
    try {
      const response = await fetch("http://localhost:5000/", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`, // Make sure the token is correctly passed
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      console.error("There was an error fetching the data!", error);
    }
  };

  return (
    <>
      <Helmet>
        <title>{"Home - Stack Overflow"}</title>
      </Helmet>
      <div>
        <Link to="/signup">Sign Up</Link>
      </div>
      <div>
        <Link to="/signin">Sign In</Link>
      </div>
      <Icon />
      <p>This is Home</p>
      <p>{message}</p> {/* Display the message here */}
    </>
  );
};

export default Home;
