import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import Navbar from '../components/navbar';
import '../style/style.css';
import BACKEND_URL from "../api";
import { Link } from 'react-router-dom';

const Chat = () => {
  const [message, setMessage] = useState('');
  const [book, setBook] = useState(null);
  const [messages, setMessages] = useState([]);
  const [userId, setUserId] = useState(null);       // Current user id

  useEffect(() => {
    const fetchUserAndRecentBook = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          console.error("No access token found.");
          return;
        }

        // Fetch user profile
        const userResponse = await fetch(`${BACKEND_URL}/user/profile`, {
          method: 'GET',
          headers: { Authorization: `Bearer ${token}` }
        });

        const userData = await userResponse.json();
        setUserId(userData.id);

        // Fetch user's most recently finished book
        const bookResponse = await fetch(`${BACKEND_URL}/api/chat/user/${userData.id}/lastread`);
        const bookData = await bookResponse.json();
        if (bookResponse.ok) {
          setBook(bookData);
          fetchMessages(bookData._id, userData.id);
        } else {
          console.error('Error fetching recent book:', bookData.error);
        }

      } catch (error) {
        console.error('Error fetching user or book:', error);
      }
    };

    fetchUserAndRecentBook();
  }, []);

  const fetchMessages = async (bookId, currentUserId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/chat/${bookId}/messages`);
      const data = await response.json();
      if (response.ok) {
        const shaped = data.map(msg => ({
          id: msg._id,
          text: msg.message_text,
          username: msg.username || "Anon",
          isMine: msg.user_id === currentUserId,
        }));
        setMessages(shaped);
      } else {
        console.error("Error fetching messages:", data.error);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };
  
  const handleMessageChange = (e) => {
    setMessage(e.target.value);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || !book || !userId) return;

    try {
      const response = await fetch(`${BACKEND_URL}/api/chat/${book._id}/send`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          message_text: message,
        }),
      });

      if (response.ok) {
        setMessage('');
        fetchMessages(book._id, userId);  // Refresh chat after sending
      } else {
        const data = await response.json();
        console.error('Error sending message:', data.error);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div className="chat-page-container">
      <div className="chat-content">
        {/* Left section - Book Info */}
        <div className="book-section">
        <div className="book-cover">
          {book?.cover_image && (
            <img src={book.cover_image} alt={book.title} />
          )}
        </div>
          <div className="book-details">
            {book ? (
              <>
                <h2 className="book-title">{book.title}</h2>
                <p className="book-author">{book.author} {book.year ? `, ${book.year}` : ''}</p>
                <p className="book-description">{book.summary?.split(' ').slice(0, 100).join(' ') + (book.summary?.split(' ').length > 100 ? '...' : '')}</p>
              </>
            ) : (
              <p>Loading book information...</p>
            )}
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
            <textarea
              type="text"
              value={message}
              onChange={handleMessageChange}
              placeholder="Start chatting ..."
              className="message-input"
            />
            <button type="submit" className="send-button">
              <ChevronRight size={20} />
            </button>
          </form>
          
        </div>
      </div>
      <Navbar />
    </div>
  );
};

export default Chat;