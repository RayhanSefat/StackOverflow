import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const isAuthenticated = Boolean(localStorage.getItem('token')); // Check your authentication logic here
  return isAuthenticated ? children : <Navigate to="/signin" />;
};

export default ProtectedRoute;
