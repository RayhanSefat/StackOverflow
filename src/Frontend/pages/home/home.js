import React, { useEffect, useState } from "react";
import { Helmet } from 'react-helmet';
import Icon from "../../templates/icon"; // Adjust the import path as necessary
import { Link } from 'react-router-dom';

const Home = () => {
  const [message, setMessage] = useState("");

  useEffect(() => {
    // Fetch data from the backend API
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:5000/"); // Update the URL if needed
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setMessage(data.message);
      } catch (error) {
        console.error("There was an error fetching the data!", error);
      }
    };

    fetchData();
  }, []);

  return (
    <>
      <Helmet>
        <title>{'Home - Stack Overflow'}</title>
      </Helmet>
      <div>
        <Link to="/signup">Sign Up</Link>
      </div>
      <div>
        <Link to="/signin">Sign In</Link>
      </div>
      <Icon />
      <p>This is Home</p>
      <p>{message}</p> 
    </>
  );
};

export default Home;
