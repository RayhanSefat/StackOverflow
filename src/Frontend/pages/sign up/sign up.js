import React, { useState } from "react";
import axios from "axios";

const SignUp = () => {
  const [formData, setFormData] = useState({
    fname: "",
    lname: "",
    email: "",
    username: "",
    password: "",
    retypedPassword: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    if (formData.password !== formData.retypedPassword) {
      alert("Passwords do not match");
      return;
    }

    axios
      .post("http://localhost:5000/signup", formData)
      .then((response) => {
        alert(response.data.message);
      })
      .catch((error) => {
        console.error("There was an error!", error);
      });
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="fname"
        placeholder="First Name"
        onChange={handleChange}
      />
      <br />
      <input
        type="text"
        name="lname"
        placeholder="Last Name"
        onChange={handleChange}
      />
      <br />
      <input
        type="email"
        name="email"
        placeholder="Email"
        onChange={handleChange}
      />
      <br />
      <input
        type="text"
        name="username"
        placeholder="Username"
        onChange={handleChange}
      />
      <br />
      <input
        type="password"
        name="password"
        placeholder="Password"
        onChange={handleChange}
      />
      <br />
      <input
        type="password"
        name="retypedPassword"
        placeholder="Retype Password"
        onChange={handleChange}
      />
      <br />
      <button type="submit">Sign Up</button>
    </form>
  );
};

export default SignUp;
