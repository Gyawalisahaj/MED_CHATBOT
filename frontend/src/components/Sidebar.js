import React from 'react';

function Sidebar({ open, onToggle, onNewChat, onClearHistory, sessionId }) {
  return (
    <>
      <button className="sidebar-toggle" onClick={onToggle}>
        ☰
      </button>
      <aside className={`sidebar ${open ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>🩺 MediQuery</h2>
        </div>

        <button className="new-chat-btn" onClick={onNewChat}>
          ➕ New Chat
        </button>

        <div className="sidebar-section">
          <h3>Session</h3>
          <p className="session-id">{sessionId.substring(0, 8)}...</p>
        </div>

        <div className="sidebar-section">
          <h3>Quick Links</h3>
          <ul>
            <li>📚 Medical Topics</li>
            <li>💊 Drugs & Medications</li>
            <li>🔬 Lab Values</li>
            <li>❓ FAQ</li>
          </ul>
        </div>

        <button className="clear-history-btn" onClick={onClearHistory}>
          🗑️ Clear History
        </button>

        <div className="sidebar-footer">
          <p>Powered by Groq + LangChain</p>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
