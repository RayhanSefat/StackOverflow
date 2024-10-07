import React, { useState } from "react";
import axios from "axios";
import Icon from "../../templates/icon";

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
    <>
      <Icon />
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="fname">First Name:</label>
          <br />
          <input
            type="text"
            name="fname"
            id="fname"
            placeholder="First Name"
            onChange={handleChange}
          />
        </div>
        <br />
        <div>
          <label htmlFor="lname">Last Name:</label>
          <br />
          <input
            type="text"
            name="lname"
            id="lname"
            placeholder="Last Name"
            onChange={handleChange}
          />
        </div>
        <br />
        <div>
          <label htmlFor="email">Email:</label>
          <br />
          <input
            type="email"
            name="email"
            id="email"
            placeholder="Email"
            onChange={handleChange}
          />
        </div>
        <br />
        <div>
          <label htmlFor="username">Username:</label>
          <br />
          <input
            type="text"
            name="username"
            id="username"
            placeholder="Username"
            onChange={handleChange}
          />
        </div>
        <br />
        <div>
          <label htmlFor="password">Password:</label>
          <br />
          <input
            type="password"
            name="password"
            id="password"
            placeholder="Password"
            onChange={handleChange}
          />
        </div>
        <br />
        <div>
          <label htmlFor="retypedPassword">Retype Password:</label>
          <br />
          <input
            type="password"
            name="retypedPassword"
            id="retypedPassword"
            placeholder="Retype Password"
            onChange={handleChange}
          />
        </div>
        <br />
        <button type="submit">Sign Up</button>
      </form>
    </>
  );
};

export default SignUp;
