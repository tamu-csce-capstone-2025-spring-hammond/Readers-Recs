import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, PlusCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import '../style/style.css';
import Navbar from '../components/navbar';
import EditProfile from '../components/edit-profile';
import BACKEND_URL from "../api";

const Profile = () => {
  const [user, setUser] = useState(null);
  const [bookshelf, setBookshelf] = useState({
    currentRead: null,
    booksRead: [],
    toReadShelf: [],
  });
  const [loading, setLoading] = useState(true);
  const [editProfilePopup, setEditProfilePopup] = useState(false);

  
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
        const profileResponse = await fetch(`${BACKEND_URL}/user/profile`, {
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
          const response = await fetch(`${BACKEND_URL}/shelf/api/user/${userId}/${url}`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          if (response.ok) {
            const data = await response.json();
            if (key === "currentRead" && data) {
              const pageRes = await fetch(`${BACKEND_URL}/shelf/api/user/${userId}/bookshelf/${data._id}/current-page`);
              if (pageRes.ok) {
                const pageData = await pageRes.json();
                data.current_page = pageData.page_number;
                data.progress = Math.round((pageData.page_number / data.page_count) * 100);
              }
            }
            setBookshelf((prev) => ({ ...prev, [key]: data }));            
          }
        }
      } catch (error) {
        console.error('Error fetching bookshelf data:', error);
      }
    };
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No token found');
      setLoading(false);
      return;
    }
    try {
      const profileResponse = await fetch(`${BACKEND_URL}/user/profile`, {
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
        const response = await fetch(`${BACKEND_URL}/shelf/api/user/${userId}/${url}`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          if (key === "currentRead" && data) {
            const pageRes = await fetch(`${BACKEND_URL}/shelf/api/user/${userId}/bookshelf/${data._id}/current-page`);
            if (pageRes.ok) {
              const pageData = await pageRes.json();
              data.current_page = pageData.page_number;
              data.progress = Math.round((pageData.page_number / data.page_count) * 100);
            }
          }
          setBookshelf((prev) => ({ ...prev, [key]: data }));          
        }
      }
    } catch (error) {
      console.error('Error fetching bookshelf data:', error);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Error: User profile not found</div>;

  const scrollBooks = (shelfId, direction) => {
    const container = document.getElementById(shelfId);
    if (container) {
      const scrollAmount = 300 * direction; // Adjust for smooth scrolling
      container.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    window.location.href = '/';
  };

  const handleEditProfile = () => {
    setEditProfilePopup(true);
  }
  const handleCloseEditProfile = () => {
    setEditProfilePopup(false);
  }

  const handleDeleteBook = async (bookId, shelfKey) => {
    // if (!user) return;
    console.log("In delete book function")
    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(`${BACKEND_URL}/shelf/api/user/${user.id}/bookshelf/${bookId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      if (response.ok) {
        // Remove book from local state
        console.log("BOOK DELETED")
        alert(`Deleted book!`);
        setBookshelf((prev) => ({
          ...prev,
          [shelfKey]: prev[shelfKey].filter((book) => book._id !== bookId),
        }));
      } else {
        console.error('Failed to delete book:', data.error);
      }
    } catch (error) {
      console.error('Error deleting book:', error);
    }
  }


  const titleLength = bookshelf.currentRead?.title.length || 0;
  const fontSize = `${Math.max(16, Math.min(28, titleLength / 4))}px`;

  return (
    <div className="profile-container">
      <div className="profile-inner">
        <div className="profile-top">
          <div className="profile-picture" style={{ backgroundImage: `url(${user.profile_picture})` }}></div>
          <div className="profile-info">
            <h1 className="profile-name">{user.name}</h1>
            <h2 className="profile-username">{user.username}</h2>
            <p className="profile-member-since">Member Since 2025</p>
            <div className="profile-buttons">
              <button className="edit-profile-button" onClick={handleEditProfile}>Edit Profile</button>
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
                    <div className="progress-indicator" style={{ height: `${bookshelf.currentRead?.progress ?? 0}%`  }}></div>
                  </div>
                </div>
                <div className="current-book-title" style={{ fontSize }}>
                  {bookshelf.currentRead?.title}
                </div>
              </div>
            ) : (
              <div>No current book</div>
            )}
          </div>
          <div className="profile-bottom-right">
  {[{ key: 'booksRead', title: 'Books Read' }, { key: 'toReadShelf', title: 'To-Read Shelf' }].map(({ key, title }) => (
    <div className="bookshelf-section" key={key}>
      <h2 className="section-title shelves">{title}</h2>
      
      {bookshelf[key].length > 0 ? (
        <>
          <div className="books-grid" id={key}>
            {bookshelf[key].map((book, index) => (
              <div key={`${key}-${index}`} className="book-cover-profile">
                <img src={book.cover_image} alt={book.title} />
                <button className="book-delete-button" onClick={() => handleDeleteBook(book._id, key)}>X</button>
                <div className="book-title">{book.title}</div>
              </div>
            ))}
          </div>
          <div className="scroll-buttons">
            <button className="scroll-button left" onClick={() => scrollBooks(key, -1)}><ChevronLeft size={24} /></button>
            <button className="scroll-button right" onClick={() => scrollBooks(key, 1)}><ChevronRight size={24} /></button>
          </div>
        </>
      ) : (
        <p>
          <Link to="/search" className="add-more-card">
                      <div className="add-more-content">
                        <PlusCircle size={24} />
                        <span>Fill your shelf!</span>
                      </div>
                    </Link>
        </p>
      )}
    </div>
  ))}
</div>

        </div>
      </div>
      {editProfilePopup && (
        <EditProfile user={user} onClose={handleCloseEditProfile} refreshUser={fetchUserProfile}/>

      )}
      <Navbar />
    </div>
  );
};

export default Profile;

