import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Icon from "../../templates/icon"; // Adjust the import as necessary

const SignUp = () => {
  const [formData, setFormData] = useState({
    fname: "",
    lname: "",
    email: "",
    username: "",
    password: "",
    retypedPassword: "",
  });
  const [errorMessage, setErrorMessage] = useState(""); // For displaying errors
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    // Basic form validation
    const { password, retypedPassword } = formData;
    if (password !== retypedPassword) {
      setErrorMessage("Passwords do not match");
      return;
    }

    try {
      const response = await fetch("http://localhost:5001/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setErrorMessage(errorData.message || "An error occurred. Please try again.");
        return;
      }

      // Redirect to sign in or home page after successful signup
      navigate("/signin");
    } catch (error) {
      console.error("Error during signup process:", error);
      setErrorMessage("An unexpected error occurred. Please try again.");
    }
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
        {errorMessage && <p className="error-message">{errorMessage}</p>}
      </form>
    </>
  );
};

export default SignUp;
