import { createSlice } from '@reduxjs/toolkit';
import { authAPI } from '../services/api';

const initialState = {
  user: null,
  token: localStorage.getItem('access_token') || null,
  refreshToken: localStorage.getItem('refresh_token') || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // Login action
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    // Set user info after successful login/register
    setUser: (state, action) => {
      const { user, access_token, refresh_token } = action.payload;
      state.user = user;
      state.token = access_token;
      state.refreshToken = refresh_token || state.refreshToken;
      state.isAuthenticated = true;
      state.error = null;
      if (access_token) localStorage.setItem('access_token', access_token);
      if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
    },
    // Logout action
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
    // Check if user is already logged in
    initializeAuth: (state) => {
      const token = localStorage.getItem('access_token');
      const refresh = localStorage.getItem('refresh_token');
      if (token) {
        state.token = token;
        state.refreshToken = refresh;
        state.isAuthenticated = true;
      }
    },
  },
});

export const { setUser, logout, setLoading, setError, initializeAuth } = authSlice.actions;
export default authSlice.reducer;

// Async thunk to fetch current user using stored token (if any)
export const fetchCurrentUser = () => async (dispatch) => {
  let token = localStorage.getItem('access_token');
  const refresh = localStorage.getItem('refresh_token');
  if (!token && !refresh) return;

  try {
    dispatch(setLoading(true));

    // If access token missing or expired, try refresh
    if (!token && refresh) {
      const refreshed = await authAPI.refreshToken(refresh);
      token = refreshed.access_token;
      const newRefresh = refreshed.refresh_token;
      dispatch(
        setUser({
          user: null,
          access_token: token,
          refresh_token: newRefresh,
        })
      );
    }

    // Try fetching current user with valid token
    const data = await authAPI.getCurrentUser();
    dispatch(
      setUser({
        user: { email: data.email, id: data.id },
        access_token: token,
      })
    );
  } catch (err) {
    // Token may be invalid; clear it
    dispatch(logout());
  } finally {
    dispatch(setLoading(false));
  }
};
