import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import './styles/App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1/chat';

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => {
    // Load from localStorage or create new
    const saved = localStorage.getItem('sessionId');
    return saved || uuidv4();
  });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);

  // Save session ID to localStorage
  useEffect(() => {
    localStorage.setItem('sessionId', sessionId);
  }, [sessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load chat history on mount
  useEffect(() => {
    loadChatHistory();
  }, [sessionId]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API_URL.replace('/query', '')}/history/${sessionId}`);
      // Reverse to show oldest first
      const history = response.data.reverse().map((item) => ({
        id: item.id,
        type: 'history',
        message: item.message,
        response: item.response,
        sources: item.sources || [],
        timestamp: item.timestamp,
      }));
      setMessages(history);
    } catch (error) {
      console.log('No existing chat history found');
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      // Send to backend
      const response = await axios.post(API_URL, {
        message,
        session_id: sessionId,
      });

      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        message: response.data.answer,
        sources: response.data.sources,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        message: 'Failed to process your query. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setSessionId(uuidv4());
    setMessages([]);
  };

  const handleClearHistory = async () => {
    try {
      await axios.delete(`${API_URL.replace('/query', '')}/history/${sessionId}`);
      setMessages([]);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  return (
    <div className="app">
      <Sidebar
        open={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={handleNewChat}
        onClearHistory={handleClearHistory}
        sessionId={sessionId}
      />

      <main className="main-content">
        <header className="app-header">
          <div className="header-content">
            <h1>🩺 MediQuery Assistant</h1>
            <p>Medical Knowledge Base Powered by RAG</p>
          </div>
        </header>

        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <h2>Welcome to MediQuery AI</h2>
                <p>Ask any medical question and get answers backed by medical literature.</p>
                <div className="suggestions">
                  <button
                    onClick={() =>
                      handleSendMessage('What are the symptoms of hypertension?')
                    }
                  >
                    Hypertension Symptoms
                  </button>
                  <button
                    onClick={() =>
                      handleSendMessage('What is the pathophysiology of diabetes?')
                    }
                  >
                    Diabetes Pathophysiology
                  </button>
                  <button
                    onClick={() =>
                      handleSendMessage('How is pneumonia treated?')
                    }
                  >
                    Pneumonia Treatment
                  </button>
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {loading && (
              <div className="message assistant-message">
                <div className="loading-spinner">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>Searching medical database...</p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={loading}
        />
      </main>
    </div>
  );
}

export default App;
