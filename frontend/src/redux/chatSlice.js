import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  messages: [], // Array of {id, text, sender, timestamp}
  typing: false, // Show typing indicator
  loading: false,
  error: null,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    // Add a new message
    addMessage: (state, action) => {
      state.messages.push({
        id: Date.now(),
        text: action.payload.text,
        sender: action.payload.sender, // 'user' or 'bot'
        timestamp: new Date().toISOString(),
      });
    },
    // Show/hide typing indicator
    setTyping: (state, action) => {
      state.typing = action.payload;
    },
    // Clear all messages
    clearMessages: (state) => {
      state.messages = [];
    },
    // Set all messages
    setMessages: (state, action) => {
      state.messages = action.payload;
    },
    // Loading and error states
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  addMessage,
  setTyping,
  clearMessages,
  setMessages,
  setLoading,
  setError,
} = chatSlice.actions;

export default chatSlice.reducer;
