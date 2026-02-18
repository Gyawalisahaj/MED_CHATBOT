import React, { useState } from 'react';

function ChatInput({ onSendMessage, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a medical question... (e.g., What is hypertension?)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={disabled}
          autoFocus
        />
        <button
          type="submit"
          className="send-button"
          disabled={disabled || !input.trim()}
        >
          {disabled ? '⏳' : '📤'} Send
        </button>
      </div>
      <p className="disclaimer">
        ⚠️ This is for educational purposes only. Always consult healthcare professionals for medical advice.
      </p>
    </form>
  );
}

export default ChatInput;
