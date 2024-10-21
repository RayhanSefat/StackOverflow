import React, { useState, useEffect } from "react";
import axios from "axios";
import { Helmet } from "react-helmet";
import Icon from "../../templates/icon"; // Adjust the import path as necessary
import { Link } from "react-router-dom";
import "./home.css";

const Home = () => {
  const [content, setContent] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  // Fetch the username from the backend (or local storage/JWT token)
  useEffect(() => {
    const fetchUsername = async () => {
      try {
        const token = localStorage.getItem("token"); // Assuming token is stored in localStorage
        console.log("Token = ", token);
        const response = await axios.get("http://localhost:5000/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setUsername(response.data.message.split(" ")[1]); // Extract username from the message
      } catch (err) {
        setError("Error fetching user information.");
      }
    };

    fetchUsername();
  }, []);

  // Handle file selection
  const onFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!content || !file) {
      setError("Please fill in all fields and choose a file.");
      return;
    }

    const formData = new FormData();
    formData.append("content", content);
    formData.append("file", file);
    formData.append("username", username);

    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://localhost:5000/upload",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setMessage(response.data.message);
      setContent("");
      setFile(null);
    } catch (err) {
      setError("Error occurred while uploading the file.");
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
      <div className="home-container">
        <h2>Welcome, {username}</h2>

        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label htmlFor="content">Post Content:</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter your content here"
              className="form-control"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="file">Upload a file:</label>
            <input
              type="file"
              id="file"
              onChange={onFileChange}
              className="form-control"
              accept=".c,.cpp,.java,.py,.js"
              required
            />
          </div>

          {error && <p className="error-message">{error}</p>}
          {message && <p className="success-message">{message}</p>}

          <button type="submit" className="btn-submit">
            Submit
          </button>
        </form>
      </div>
    </>
  );
};

export default Home;
