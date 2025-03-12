import React, { useState } from 'react';
import { ChevronRight, Search, BookOpen, User } from 'lucide-react';
import Navbar from '../components/navbar';
import '../style/style.css';

const Chat = () => {
  const [message, setMessage] = useState('');
    
  // Placeholder data
  const book = {
    title: "Book Title",
    author: "Author",
    year: "Year",
    description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis vestibulum a lectus at auctor. Quisque et interdum mi, in efficitur magna. Maecenas massa sapien, facilisis vitae finibus at, facilisis convallis velit. Aenean sodales turpis nec ornare mollis."
  };
  
  const messages = [
    { id: 1, text: "Message", username: "Username", isMine: false },
    { id: 2, text: "Message", username: "Username", isMine: true },
    { id: 3, text: "Message", username: "Username", isMine: false }
  ];
  
  const handleMessageChange = (e) => {
    setMessage(e.target.value);
  };
  
  const handleSendMessage = (e) => {
    e.preventDefault();
    if (message.trim()) {
      // Logic to send message would go here
      setMessage('');
    }
  };
  
  return (
    <div className="chat-page-container">
      <div className="chat-content">
        {/* Left section - Book Info */}
        <div className="book-section">
          <div className="book-cover"></div>
          <div className="book-details">
            <h2 className="book-title">{book.title}</h2>
            <p className="book-author">{book.author}, {book.year}</p>
            <p className="book-description">{book.description}</p>
          </div>
        </div>
        
        {/* Right section - Chat */}
        <div className="chat-section">
          <div className="chat-messages">
            {messages.map(message => (
              <div
                key={message.id}
                className={`message-container ${message.isMine ? 'mine' : 'other'}`}
              >
                <div className="message">
                  <p className="message-text">{message.text}</p>
                  <p className="message-username">{message.username}</p>
                </div>
              </div>
            ))}
          </div>
          
          <form className="message-input-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={message}
              onChange={handleMessageChange}
              placeholder="Type Message Here"
              className="message-input"
            />
            <button type="submit" className="send-button">
              <ChevronRight size={20} />
            </button>
          </form>
        </div>
      </div>
      <Navbar/>
    </div>
  );
};

export default Chat;