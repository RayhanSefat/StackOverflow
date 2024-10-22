import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom"; 
import { Helmet } from "react-helmet";
import Icon from "../../templates/icon";
import { Link } from "react-router-dom";
import "./home.css";

const Home = () => {
  const [content, setContent] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsername = async () => {
      try {
        const response = await axios.get("http://localhost:5000/");
        setUsername(response.data.username);
      } catch (err) {
        if (err.response && (err.response.status === 401 || err.response.status === 403)) {
          navigate("/signin");
        } else {
          setError("Error fetching user information.");
        }
      }
    };

    fetchUsername();
  }, [navigate]);

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
  };

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

    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setMessage(response.data.message);
      setContent("");
      setFile(null);
    } catch (err) {
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        navigate("/signin");
      } else {
        setError("Error occurred while uploading the file.");
      }
    }
  };

  const handleSignOut = async () => {
    try {
      await axios.post("http://localhost:5000/signout");
      navigate("/signin");
    } catch (err) {
      setError("Error occurred while signing out.");
    }
  };

  return (
    <div className="home">
      <Helmet>
        <title>Welcome, {username}!</title>
      </Helmet>
      <main>
        <div>
          <Link to="/signup">Sign Up</Link>
        </div>
        <div>
          <Link to="/signin">Sign In</Link>
        </div>
        <Icon />
        <h1>Hello, {username}!</h1>
        <button onClick={handleSignOut}>Sign Out</button> {/* Sign Out Button */}
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label htmlFor="content">Post Content:</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="file">Choose file to upload:</label>
            <input type="file" id="file" onChange={onFileChange} />
          </div>
          <button type="submit">Upload</button>
        </form>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
      </main>
    </div>
  );
};

export default Home;
