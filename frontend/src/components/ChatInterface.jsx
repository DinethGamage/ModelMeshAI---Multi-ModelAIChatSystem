import React, { useState, useRef, useEffect } from 'react';
import { chatAPI } from '../services/api';
import Message from './Message';
import PDFUpload from './PDFUpload';
import './ChatInterface.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [documentUploaded, setDocumentUploaded] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(userMessage, sessionId);
      
      // Update session ID if new
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Add assistant response to UI
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: response.response,
          metadata: response.routing_metadata,
        },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ Error: ${error.response?.data?.detail || error.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleUploadSuccess = (result) => {
    setDocumentUploaded(true);
    setSessionId(result.session_id);
    setMessages(prev => [
      ...prev,
      {
        role: 'system',
        content: `📄 PDF uploaded successfully: ${result.filename} (${result.chunks_stored} chunks stored)`,
      },
    ]);
    setShowUpload(false);
  };

  const handleNewSession = () => {
    setMessages([]);
    setSessionId(null);
    setDocumentUploaded(false);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>🤖 Multi-Model AI Chat System</h1>
        <div className="header-actions">
          {sessionId && (
            <span className="session-id">Session: {sessionId.substring(0, 8)}...</span>
          )}
          {documentUploaded && <span className="doc-indicator">📄 Document Ready</span>}
          <button onClick={() => setShowUpload(!showUpload)} className="upload-toggle">
            {showUpload ? '💬 Chat' : '📤 Upload PDF'}
          </button>
          <button onClick={handleNewSession} className="new-session-btn">
            🔄 New Session
          </button>
        </div>
      </div>

      {showUpload ? (
        <div className="upload-section">
          <PDFUpload sessionId={sessionId} onUploadSuccess={handleUploadSuccess} />
        </div>
      ) : (
        <>
          <div className="messages-container">
            {messages.length === 0 && (
              <div className="welcome-message">
                <h2>👋 Welcome!</h2>
                <p>Ask me anything! I can help with:</p>
                <ul>
                  <li>🧮 Math calculations</li>
                  <li>💻 Programming questions</li>
                  <li>✍️ Writing tasks</li>
                  <li>📄 Document analysis (upload PDF first)</li>
                  <li>💬 General conversation</li>
                </ul>
              </div>
            )}
            {messages.map((msg, index) => (
              <Message
                key={index}
                message={msg.content}
                isUser={msg.role === 'user'}
                metadata={msg.metadata}
              />
            ))}
            {loading && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <span>Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here... (Shift+Enter for new line)"
              disabled={loading}
              rows="3"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || loading}
              className="send-button"
            >
              {loading ? '⏳' : '📤'} Send
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatInterface;
