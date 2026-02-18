import React, { useState } from 'react';

function ChatMessage({ message }) {
  const [showSources, setShowSources] = useState(false);

  if (message.type === 'user') {
    return (
      <div className="message user-message">
        <div className="message-content">
          {message.message}
        </div>
      </div>
    );
  }

  if (message.type === 'error') {
    return (
      <div className="message error-message">
        <div className="message-content">
          {message.message}
        </div>
      </div>
    );
  }

  return (
    <div className="message assistant-message">
      <div className="message-content">
        <p>{message.message}</p>
        {message.sources && message.sources.length > 0 && (
          <div className="sources-section">
            <button
              className="sources-toggle"
              onClick={() => setShowSources(!showSources)}
            >
              📄 {message.sources.length} Sources
            </button>
            {showSources && (
              <div className="sources-list">
                {message.sources.map((source, idx) => (
                  <div key={idx} className="source-item">
                    {source}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
