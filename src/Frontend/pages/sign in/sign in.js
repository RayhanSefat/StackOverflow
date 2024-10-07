import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const SignIn = () => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    axios
      .post("http://localhost:5000/signin", formData)
      .then((response) => {
        alert(response.data.message); // Alert on successful sign-in
      })
      .catch((error) => {
        alert("Invalid login"); // Alert on error
        console.error("Error: ", error);
      });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="username"
          placeholder="Username"
          onChange={handleChange}
          required
        />{" "}
        <br />
        <input
          type="password"
          name="password"
          placeholder="Password"
          onChange={handleChange}
          required
        />{" "}
        <br />
        <button type="submit">Sign In</button>
      </form>
      <br />
      <br />
      <div>
        <Link to="/signup">Sign Up</Link>
      </div>
    </>
  );
};

export default SignIn;
