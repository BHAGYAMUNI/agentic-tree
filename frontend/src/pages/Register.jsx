import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { setUser, setLoading, setError } from '../redux/authSlice';
import { authAPI } from '../services/api';
import { isValidEmail, isValidPassword } from '../utils/treeUtils';
import '../styles/auth.css';

/**
 * Register Page
 * User registration with email and password
 * Features:
 * - Form validation
 * - Password strength checking
 * - Error handling
 * - Loading state
 * - Link to login
 */
function Register() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated, loading, error } = useSelector((state) => state.auth);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState('');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError('');

    // Validation
    if (!email.trim()) {
      setLocalError('Email is required');
      return;
    }

    if (!isValidEmail(email)) {
      setLocalError('Please enter a valid email address');
      return;
    }

    if (!password) {
      setLocalError('Password is required');
      return;
    }

    if (!isValidPassword(password)) {
      setLocalError('Password must be at least 6 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    dispatch(setLoading(true));

    try {
      const response = await authAPI.register(email, password);

      // Dispatch user data to Redux
      dispatch(
        setUser({
          user: { email: response.email, id: response.user_id },
          access_token: response.access_token,
          refresh_token: response.refresh_token,
        })
      );

      // Navigate to dashboard
      navigate('/dashboard');
    } catch (err) {
      const errorMessage = err.message || 'Registration failed. Please try again.';
      setLocalError(errorMessage);
      dispatch(setError(errorMessage));
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-content">
        <div className="auth-card">
          {/* Header */}
          <div className="auth-header">
            <div className="auth-header-icon">🌳</div>
            <h1>Create Account</h1>
            <p>Join Tree AI and start building trees</p>
          </div>

          {/* Error Message */}
          {(localError || error) && <div className="auth-error">{localError || error}</div>}

          {/* Registration Form */}
          <form className="auth-form" onSubmit={handleSubmit}>
            {/* Email Input */}
            <div className="auth-form-group">
              <label htmlFor="email">Email Address</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                disabled={loading}
                required
              />
            </div>

            {/* Password Input */}
            <div className="auth-form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                disabled={loading}
                required
              />
            </div>

            {/* Confirm Password Input */}
            <div className="auth-form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                disabled={loading}
                required
              />
            </div>

            {/* Submit Button */}
            <button type="submit" className="auth-submit-btn" disabled={loading}>
              {loading ? (
                <span className="auth-loading">
                  <span className="spinner"></span>
                  Creating account...
                </span>
              ) : (
                'Sign Up'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="auth-footer">
            Already have an account?{' '}
            <Link to="/login">
              Sign in here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;