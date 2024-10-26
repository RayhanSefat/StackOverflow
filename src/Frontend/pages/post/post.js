import React, { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
import { Helmet } from "react-helmet";
import Icon from "../../templates/icon";
import "./post.css"

const Post = () => {
  const { postId } = useParams();
  const [post, setPost] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  console.log(postId)

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const response = await axios.get(
          `http://localhost:5000/post/${postId}`
        );
        setPost(response.data);
      } catch (err) {
        setError(err.response?.data?.message || "Error fetching post content.");
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [postId]);

  return (
    <div className="post-page">
      <Helmet>
        <title>Post</title>
      </Helmet>
      <Icon />
      {loading ? (
        <p>Loading post...</p>
      ) : post ? (
        <div>
          <p>{post.description}</p>
          <pre className="file-content">{post.content}</pre>
        </div>
      ) : (
        <p>{error}</p>
      )}
    </div>
  );
};

export default Post;
