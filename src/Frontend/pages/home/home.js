import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom"; 
import { Helmet } from "react-helmet";
import Icon from "../../templates/icon";
import { Link } from "react-router-dom";
import "./home.css";

const Home = () => {
  const [description, setDescription] = useState(""); // New state for description
  const [content, setContent] = useState("");
  const [extension, setExtension] = useState("txt");
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

  const handleSaveContent = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!description || !content || !extension) {
      setError("Please fill in all fields.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/save_content", {
        description,
        content,
        extension,
      });

      setMessage(response.data.message);
      setDescription(""); // Clear description after saving
      setContent(""); // Clear content after saving
      setExtension("txt"); // Reset extension to default
    } catch (err) {
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        navigate("/signin");
      } else {
        setError("Error occurred while saving content.");
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
        <button onClick={handleSignOut}>Sign Out</button>
        <form onSubmit={handleSaveContent} className="content-form">
          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="content">Paste Content:</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label htmlFor="extension">Select File Extension:</label>
            <select id="extension" value={extension} onChange={(e) => setExtension(e.target.value)}>
              <option value="txt">.txt</option>
              <option value="c">.c</option>
              <option value="cpp">.cpp</option>
              <option value="css">.css</option>
              <option value="js">.js</option>
              <option value="py">.py</option>
            </select>
          </div>
          <button type="submit">Post</button>
        </form>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
      </main>
    </div>
  );
};

export default Home;
