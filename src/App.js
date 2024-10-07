import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import SignUp from './Frontend/pages/sign up/sign up'; // Adjust the path as necessary
import SignIn from './Frontend/pages/sign in/sign in'; // Adjust the path as necessary
import Home from './Frontend/pages/home/home'; // Adjust the path as necessary

const App = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/signin" element={<SignIn />} />
      </Routes>
    </div>
  );
};

export default App;
