import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState([]);
  const [response, setResponse] = useState('');
  const [chatEnded, setChatEnded] = useState(false);
  const [loading, setLoading] = useState(false); // Add loading state

  useEffect(() => {
    // Fetch initial greeting from the server
    const fetchGreeting = async () => {
      try {
        const res = await axios.post('http://localhost:5000/chat', {
          message: '',
          history: [],
        });
        setResponse(res.data.response);
        setHistory(res.data.history);
      } catch (error) {
        console.error('Error fetching greeting:', error);
      }
    };

    fetchGreeting();
  }, []);

  const handleSend = async () => {
    try {
      if (chatEnded) return;

      const newHistory = [...history, [message, '']];
      setHistory(newHistory); // Update history with user's message instantly
      setMessage('');
      setLoading(true); // Set loading to true when message is sent

      const res = await axios.post('http://localhost:5000/chat', {
        message,
        history: newHistory,
      });

      const updatedHistory = newHistory.map((entry, index) => {
        if (index === newHistory.length - 1) {
          return [entry[0], res.data.response];
        }
        return entry;
      });

      setHistory(updatedHistory);
      setResponse(res.data.response);
      setLoading(false); // Set loading to false when response is received
    } catch (error) {
      console.error('Error sending message:', error);
      setLoading(false); // Ensure loading is false if there's an error
    }
  };

  const handleClearChat = () => {
    setHistory([]);
    setResponse('');
    setMessage('');
    setChatEnded(false);
  };

  const handleEndChat = () => {
    setChatEnded(true);
  };

  const handleRestartChat = () => {
    setHistory([]);
    setResponse('');
    setMessage('');
    setChatEnded(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="App">
      <div className="chat-container">
        <h1>Dr. Mandy</h1>
        <div className="chat-history">
          {history.map((entry, index) => (
            <div key={index} className="message">
              {entry[0] && (
                <div className="user-message">
                  <img src="https://via.placeholder.com/40" alt="User Icon" className="avatar" />
                  <div className="message-content">
                    <strong>User:</strong> {entry[0]}
                  </div>
                </div>
              )}
              {entry[1] && (
                <div className="assistant-message">
                  <img src="https://via.placeholder.com/40" alt="Assistant Icon" className="avatar" />
                  <div className="message-content">
                    <strong>Assistant:</strong> {entry[1]}
                  </div>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message assistant-message">
              <img src="https://via.placeholder.com/40" alt="Assistant Icon" className="avatar" />
              <div className="message-content loading-dots">
                <span>.</span><span>.</span><span>.</span>
              </div>
            </div>
          )}
          {chatEnded && (
            <div className="message response">
              Chat has ended.{' '}
              <button className="restart-btn" onClick={handleRestartChat}>
                Restart Chat
              </button>
            </div>
          )}
        </div>
        <div className="chat-input">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={chatEnded ? 'Chat has ended' : 'Type your message here...'}
            disabled={chatEnded}
          />
          <div className="buttons">
            {!chatEnded && <button onClick={handleSend}>Send</button>}
            <button className="clear-btn" onClick={handleClearChat}>
              Clear Chat
            </button>
            {!chatEnded && <button onClick={handleEndChat}>End Chat</button>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
