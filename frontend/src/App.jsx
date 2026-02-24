import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { initializeAuth } from './redux/authSlice';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import './styles/theme.css';

/**
 * Main App Component
 * Handles routing and authentication initialization
 * Routes:
 * - / -> Login (public)
 * - /register -> Register (public)
 * - /dashboard -> Dashboard (protected)
 */
function App() {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);

  // Initialize auth state and fetch current user if token exists
  useEffect(() => {
    dispatch(initializeAuth());
    // fetchCurrentUser is async; import it from authSlice
    import('./redux/authSlice').then((m) => {
      if (m.fetchCurrentUser) dispatch(m.fetchCurrentUser());
    });
  }, [dispatch]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        {/* Default: send unauthenticated users to register so new users see sign-up first */}
        <Route path="/" element={<Navigate to="/register" replace />} />

        {/* Protected Routes */}
        <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/register" replace />} />

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/register" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;