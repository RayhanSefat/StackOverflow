import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import Home from './pages/sign in/sign in'
import SignIn from "./pages/sign up/sign up";
import SignUp from "./pages/sign up/sign up";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <SignUp />
);
reportWebVitals();
