import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Helmet } from "react-helmet";
import Icon from "../../templates/icon";
import { Link } from "react-router-dom";
import "./home.css";

const Home = () => {
  const [description, setDescription] = useState("");
  const [content, setContent] = useState("");
  const [extension, setExtension] = useState("txt");
  const [message, setMessage] = useState("");
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [posts, setPosts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsername = async () => {
      try {
        const response = await axios.get("http://localhost:5000/");
        setUsername(response.data.username);
      } catch (err) {
        if (
          err.response &&
          (err.response.status === 401 || err.response.status === 403)
        ) {
          setUsername(""); // Ensure username is reset if not logged in
        } else {
          setError("Error fetching user information.");
        }
      }
    };

    const fetchPosts = async () => {
      try {
        const response = await axios.get("http://localhost:5000/posts");
        setPosts(response.data.posts);
      } catch (err) {
        setError("Error fetching posts.");
      }
    };

    fetchUsername();
    if (username) {
      fetchPosts();
    }
  }, [navigate, username]);

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
      setDescription("");
      setContent("");
      setExtension("txt");

      // Fetch the updated posts after saving content
      const postsResponse = await axios.get("http://localhost:5000/posts");
      setPosts(postsResponse.data.posts);
    } catch (err) {
      if (
        err.response &&
        (err.response.status === 401 || err.response.status === 403)
      ) {
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
        <title>{username ? `Welcome, ${username}!` : "Home"}</title>
      </Helmet>
      <Icon />
      <main>
        {(username === "Guest") ? (
          <div>
            <div>
              <Link to="/signup">Sign Up</Link>
            </div>
            <div>
              <Link to="/signin">Sign In</Link>
            </div>
          </div>
        ) : (
          <>
            <div>
              <Link to="/notifications">Notifications</Link>
            </div>
            <h1>Hello, {username}!</h1>
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
                <select
                  id="extension"
                  value={extension}
                  onChange={(e) => setExtension(e.target.value)}
                >
                  <option value="txt">.txt</option>
                  <option value="c">.c</option>
                  <option value="cpp">.cpp</option>
                  <option value="css">.css</option>
                  <option value="js">.js</option>
                  <option value="py">.py</option>
                </select>
              </div>
              <button type="submit">Save Content</button>
            </form>
            {error && <p className="error-message">{error}</p>}
            {message && <p className="success-message">{message}</p>}
            <h2>Recent Posts:</h2>
            <div className="post-list">
              {posts.map((post, index) => (
                <div key={index} className="post-item">
                  <h3>{post.username}</h3>
                  <p className="post-description">{post.description}</p>
                  <pre className="file-content">{post.content}</pre>
                  <small>
                    {new Date(
                      new Date(post.timestamp).setHours(
                        new Date(post.timestamp).getHours() - 6
                      )
                    ).toLocaleString()}
                  </small>
                </div>
              ))}
            </div>
            <button onClick={handleSignOut}>Sign Out</button>
          </>
        )}
      </main>
    </div>
  );
};

export default Home;
