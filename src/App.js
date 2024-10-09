import React from 'react';
import { Route, Routes } from 'react-router-dom';
import SignUp from './Frontend/pages/sign up/sign up'; // Adjust the path as necessary
import SignIn from './Frontend/pages/sign in/sign in'; // Adjust the path as necessary
import Home from './Frontend/pages/home/home'; // Your Home component
import ProtectedRoute from './Frontend/ProtectedRoute'; // Protected route component

function App() {
  return (
    <Routes>
      {/* Sign Up Route */}
      <Route path="/signup" element={<SignUp />} />
      
      {/* Sign In Route */}
      <Route path="/signin" element={<SignIn />} />

      {/* Protected Home Route */}
      <Route path="/" element={
        <ProtectedRoute>
          <Home />
        </ProtectedRoute>
      } />
    </Routes>
  );
}

export default App;
