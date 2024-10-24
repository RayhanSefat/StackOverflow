import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

const SignIn = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState(""); // For displaying errors
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Clear any previous error messages
    setErrorMessage("");

    // Basic form validation
    if (!username || !password) {
      setErrorMessage("Username and password are required");
      return;
    }

    try {
      console.log("Sending login request:", { username, password });

      const response = await fetch("http://localhost:5000/signin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        // Check if it’s an authentication failure (401) or other issues (500)
        const errorData = await response.json();
        if (response.status === 401) {
          setErrorMessage(errorData.message || "Invalid username or password");
        } else {
          setErrorMessage(
            errorData.message || "An error occurred. Please try again later."
          );
        }
        return;
      }

      const data = await response.json();
      console.log("Login successful");

      // Navigate to home or dashboard after successful login
      navigate("/");
    } catch (error) {
      console.error("Error during sign-in process:", error);
      setErrorMessage("An unexpected error occurred. Please try again.");
    }
  };

  return (
    <div className="signin-container">
      <h2>Sign In</h2>
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Sign In</button>

        <p>Don't have and account? <Link to="/signup">Sign Up</Link></p>
      </form>
    </div>
  );
};

export default SignIn;
