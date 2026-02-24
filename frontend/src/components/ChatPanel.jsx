import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addMessage, clearMessages, setTyping } from '../redux/chatSlice';
import { chatAPI, treeAPI } from '../services/api';
import { formatTime, convertTreeToFlowData } from '../utils/treeUtils';
import { setTreeVisualization } from '../redux/treeSlice';
import '../styles/chat-panel.css';

/**
 * ChatPanel Component
 * AI-powered chat interface for tree operations and discussions
 * Features:
 * - Send/receive messages
 * - Typing indicator animation
 * - Auto-scroll to latest message
 * - Export chat as JSON
 * - Clear chat history
 */
function ChatPanel() {
  const dispatch = useDispatch();
  const { selectedTree } = useSelector((state) => state.tree);
  const { messages, typing } = useSelector((state) => state.chat);

  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, typing]);

  // Refresh tree visualization after chat-based operations
  const refreshTreeVisualization = async () => {
    if (!selectedTree) return;
    try {
      const response = await treeAPI.getTree(selectedTree.id);
      const treeData = response.tree_data;
      const { nodes, edges } = convertTreeToFlowData(treeData);
      dispatch(setTreeVisualization({ nodes, edges }));
    } catch (err) {
      console.error('Failed to refresh tree after chat:', err);
    }
  };

  // ==================== SEND MESSAGE ====================
  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!selectedTree) {
      alert('Please select or create a tree first');
      return;
    }

    if (!inputValue.trim()) {
      return;
    }

    const userMessage = inputValue.trim();
    setInputValue('');
    setLoading(true);

    // Add user message to Redux
    dispatch(addMessage({ text: userMessage, sender: 'user' }));

    // Show typing indicator
    dispatch(setTyping(true));

    try {
      // Call backend API
      const response = await chatAPI.sendMessage(selectedTree.id, userMessage);

      // Add bot response to Redux
      dispatch(addMessage({ text: response.response || response.message, sender: 'bot' }));

      // Sync latest tree structure to visualization (for insert/delete/traversal commands)
      await refreshTreeVisualization();
    } catch (error) {
      console.error('Error sending message:', error);
      dispatch(addMessage({ text: 'Sorry, I encountered an error. Please try again.', sender: 'bot' }));
    } finally {
      dispatch(setTyping(false));
      setLoading(false);
    }
  };

  // ==================== CLEAR CHAT ====================
  const handleClearChat = async () => {
    if (!selectedTree) return;

    const confirmed = window.confirm('Are you sure you want to clear chat history?');
    if (!confirmed) return;

    try {
      await chatAPI.clearChat(selectedTree.id);
      dispatch(clearMessages());
    } catch (error) {
      console.error('Error clearing chat:', error);
      alert('Failed to clear chat');
    }
  };

  // ==================== EXPORT CHAT ====================
  const handleExportChat = () => {
    if (messages.length === 0) {
      alert('No messages to export');
      return;
    }

    const chatData = {
      tree: selectedTree?.name || 'Unknown Tree',
      exportedAt: new Date().toISOString(),
      messages: messages.map((msg) => ({
        sender: msg.sender,
        text: msg.text,
        timestamp: msg.timestamp,
      })),
    };

    const dataStr = JSON.stringify(chatData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `chat-export-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="chat-panel-container">
      {/* Chat Header */}
      <div className="chat-header">
        <h3>💬 AI Chat</h3>
        <div className="chat-header-actions">
          <button
            className="chat-header-btn"
            onClick={handleExportChat}
            disabled={messages.length === 0}
            title="Export chat as JSON"
          >
            📥 Export
          </button>
          <button
            className="chat-header-btn"
            onClick={handleClearChat}
            disabled={messages.length === 0}
            title="Clear chat history"
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      {/* Messages Container */}
      {messages.length === 0 && !typing ? (
        <div className="chat-messages">
          <div className="chat-empty-state">
            <div className="chat-empty-icon">💬</div>
            <p className="chat-empty-text">No messages yet. Start a conversation about your tree!</p>
          </div>
        </div>
      ) : (
        <div className="chat-messages">
          {/* Render all messages */}
          {messages.map((message) => (
            <div key={message.id} className={`chat-message ${message.sender}`}>
              <div className="chat-message-avatar">
                {message.sender === 'user' ? '👤' : '🤖'}
              </div>
              <div className="chat-message-content">
                <div className="chat-message-bubble">{message.text}</div>
                <div className="chat-message-time">{formatTime(message.timestamp)}</div>
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {typing && (
            <div className="chat-message bot">
              <div className="chat-message-avatar">🤖</div>
              <div className="chat-message-content">
                <div className="chat-typing-indicator">
                  <div className="chat-typing-dot"></div>
                  <div className="chat-typing-dot"></div>
                  <div className="chat-typing-dot"></div>
                </div>
              </div>
            </div>
          )}

          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Input Area */}
      {selectedTree ? (
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <input
              type="text"
              className="chat-input-field"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(e);
                }
              }}
              placeholder="Ask about the tree or tree operations..."
              disabled={loading || typing}
            />
            <button
              className="chat-send-btn"
              onClick={handleSendMessage}
              disabled={loading || typing || !inputValue.trim()}
              title="Send message (Ctrl+Enter)"
            >
              📤
            </button>
          </div>
        </div>
      ) : (
        <div className="chat-input-area" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
          <p>Select a tree to start chatting</p>
        </div>
      )}
    </div>
  );
}

export default ChatPanel;
