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

  // Fetch user profile and bookshelf data from the backend API
  useEffect(() => {
    const fetchUserProfile = async () => {
      const token = localStorage.getItem('access_token'); // Assuming the token is stored in localStorage
      if (!token) {
        console.error('No token found');
        setLoading(false);
        return;
      }

      try {
        // Fetch user profile data
        const profileResponse = await fetch('http://localhost:8000/user/profile', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!profileResponse.ok) {
          throw new Error('Failed to fetch user profile');
        }

        const profileData = await profileResponse.json();
        setUser(profileData); // Set the user data in state

        // Fetch bookshelf data (Books read, To-read shelf, and Currently reading)
        const userId = profileData.id; // Assuming _id is returned in the profile data
        await fetchBookshelfData(userId, token);
      } catch (error) {
        console.error('Error fetching profile or bookshelf data:', error);
      } finally {
        setLoading(false); // Stop loading
      }
    };

    const fetchBookshelfData = async (userId, token) => {
      try {
        // Fetch currently reading books
        const currentReadResponse = await fetch(`http://localhost:8000/shelf/api/user/${userId}/books/currently-reading`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (currentReadResponse.ok) {
          const currentReadData = await currentReadResponse.json();
          console.log("current read:", currentReadData)
          setBookshelf((prevState) => ({ ...prevState, currentRead: currentReadData })); // Assume we get the first book
        }

        // Fetch books read
        const booksReadResponse = await fetch(`http://localhost:8000/shelf/api/user/${userId}/books/read`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (booksReadResponse.ok) {
          const booksReadData = await booksReadResponse.json();
          setBookshelf((prevState) => ({ ...prevState, booksRead: booksReadData }));
        }

        // Fetch to-read shelf
        const toReadResponse = await fetch(`http://localhost:8000/shelf/api/user/${userId}/books/to-read`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (toReadResponse.ok) {
          const toReadData = await toReadResponse.json();
          setBookshelf((prevState) => ({ ...prevState, toReadShelf: toReadData }));
        }

      } catch (error) {
        console.error('Error fetching bookshelf data:', error);
      }
    };

    fetchUserProfile();
  }, []);

  // If user data is still loading, show a loading spinner or placeholder
  if (loading) {
    return <div>Loading...</div>;
  }

  // If no user data is found
  if (!user) {
    return <div>Error: User profile not found</div>;
  }

  // Scroll books function
  const scrollBooks = (id, direction) => {
    const container = document.getElementById(id);
    if (container) {
      const scrollAmount = 250;
      container.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' });
    }
  };

  const handleLogout = () => {
    // Clear the user’s token from localStorage
    localStorage.removeItem("access_token");

    // Redirect to the login page (or home page)
    window.location.href = "/";
  };

  return (
    <>
      <div className="profile-container">
        <div className="profile-inner">
          <div className="profile-top">
            <div className="profile-picture" style={{ backgroundImage: `url(${user.profile_picture})` }}></div>
            <div className="profile-info">
              <h1 className="profile-name">{user.name}</h1>
              <h2 className="profile-username">{user.email}</h2>
              <p className="profile-member-since">Member Since 2025</p>
              <button className="edit-profile-button">Edit Profile</button>
              <button className="edit-profile-button" onClick={handleLogout}>Logout</button>
            </div>
          </div>
          <div className="profile-bottom">
            <div className="current-read-section">
              <h2 className="section-title current-read-title">CURRENT<br />READ</h2>
              {bookshelf.currentRead ? (
                <div className="current-book">
                  <img src={bookshelf.currentRead.cover_image} alt={bookshelf.currentRead.title} className="book-cover-profile current" />
                  <div className="progress-bar">
                    <div className="progress-indicator" style={{ height: `${bookshelf.currentRead.progress}%` }}></div>
                  </div>
                </div>
              ) : (
                <div>No current book</div>
              )}
            </div>
            <div className="profile-bottom-right">
              <div className="bookshelf-section">
                <h2 className="section-title shelves">Books Read</h2>
                <div className="books-grid" id="books-read">
                  {bookshelf.booksRead.map((book, index) => (
                    <div key={`read-${index}`} className="book-cover-profile">
                      <img src={book.cover_image} alt={book.title} />
                    </div>
                  ))}
                </div>
                <button className="scroll-button left" onClick={() => scrollBooks("books-read", -1)}>
                  <ChevronLeft size={24} />
                </button>
                <button className="scroll-button right" onClick={() => scrollBooks("books-read", 1)}>
                  <ChevronRight size={24} />
                </button>
              </div>
              <div className="to-read-section">
                <h2 className="section-title shelves">To-Read Shelf</h2>
                <div className="books-grid" id="to-read">
                  {bookshelf.toReadShelf.map((book, index) => (
                    <div key={`to-read-${index}`} className="book-cover-profile">
                      <img src={book.cover_image} alt={book.title} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="app-navigation">
        <Navbar />
      </div>
    </>
  );
};

export default Profile;
