import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import '../style/style.css';
import Navbar from '../components/navbar';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [bookshelf, setBookshelf] = useState({
    currentRead: null,
    booksRead: [],
    toReadShelf: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserProfile = async () => {
      const token = localStorage.getItem('access_token');
      console.log('Token:', token);
      if (!token) {
        console.error('No token found');
        setLoading(false);
        return;
      }
      try {
        const profileResponse = await fetch('http://localhost:8000/user/profile', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!profileResponse.ok) throw new Error('Failed to fetch user profile');
        const profileData = await profileResponse.json();
        setUser(profileData);
        fetchBookshelfData(profileData.id, token);
      } catch (error) {
        console.error('Error fetching profile or bookshelf data:', error);
      } finally {
        setLoading(false);
      }
    };

    const fetchBookshelfData = async (userId, token) => {
      try {
        const endpoints = [
          { key: 'currentRead', url: `books/currently-reading` },
          { key: 'booksRead', url: `books/read` },
          { key: 'toReadShelf', url: `books/to-read` },
        ];
        for (const { key, url } of endpoints) {
          const response = await fetch(`http://localhost:8000/shelf/api/user/${userId}/${url}`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (response.ok) {
            const data = await response.json();
            setBookshelf((prev) => ({ ...prev, [key]: data }));
          }
        }
      } catch (error) {
        console.error('Error fetching bookshelf data:', error);
      }
    };

    fetchUserProfile();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Error: User profile not found</div>;

  const scrollBooks = (id, direction) => {
    const container = document.getElementById(id);
    if (container) container.scrollBy({ left: direction * 250, behavior: 'smooth' });
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    window.location.href = '/';
  };

  return (
    <div className="profile-container">
      <div className="profile-inner">
        <div className="profile-top">
          <div className="profile-picture" style={{ backgroundImage: `url(${user.profile_picture})` }}></div>
          <div className="profile-info">
            <h1 className="profile-name">{user.name}</h1>
            <h2 className="profile-username">{user.email}</h2>
            <p className="profile-member-since">Member Since 2025</p>
            <div className="profile-buttons">
              <button className="edit-profile-button">Edit Profile</button>
              <button className="edit-profile-button" onClick={handleLogout}>Logout</button>
            </div>
          </div>
        </div>
        <div className="profile-bottom">
        <div className="current-read-section">
            <h2 className="section-title current-read-title">CURRENT READ</h2>
            {bookshelf.currentRead ? (
              <div className="current-book">
                <div className="current-book-cover-progress">
                  <img src={bookshelf.currentRead.cover_image} alt={bookshelf.currentRead.title} className="book-cover-profile current" />
                  <div className="progress-bar">
                    <div className="progress-indicator" style={{ height: `${bookshelf.currentRead.progress}%` }}></div>
                  </div>
                </div>
                <div className="current-book-title">{bookshelf.currentRead.title}</div>
              </div>
            ) : (
              <div>No current book</div>
            )}
          </div>
          <div className="profile-bottom-right">
            {[{ key: 'booksRead', title: 'Books Read' }, { key: 'toReadShelf', title: 'To-Read Shelf' }].map(({ key, title }) => (
              <div className="bookshelf-section" key={key}>
                <h2 className="section-title shelves">{title}</h2>
                <div className="books-grid" id={key}>
                  {bookshelf[key].map((book, index) => (
                    <div key={`${key}-${index}`} className="book-cover-profile">
                      <img src={book.cover_image} alt={book.title} />
                      <div className="book-title">{book.title}</div>
                    </div>
                  ))}
                </div>
                <div className="scroll-buttons">
                  <button className="scroll-button left" onClick={() => scrollBooks(key, -1)}><ChevronLeft size={24} /></button>
                  <button className="scroll-button right" onClick={() => scrollBooks(key, 1)}><ChevronRight size={24} /></button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <Navbar />
    </div>
  );
};

export default Profile;

