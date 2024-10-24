import React from 'react';
import { Route, Routes } from 'react-router-dom';
import Notifications from './Frontend/pages/notifications/notifications';
import SignUp from './Frontend/pages/sign up/sign up'; 
import SignIn from './Frontend/pages/sign in/sign in'; 
import Home from './Frontend/pages/home/home'; 
import ProtectedRoute from './Frontend/ProtectedRoute'; 

function App() {
  return (
    <Routes>
      <Route path="/notifications" element={<Notifications />} />

      <Route path="/signup" element={<SignUp />} />
      
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
