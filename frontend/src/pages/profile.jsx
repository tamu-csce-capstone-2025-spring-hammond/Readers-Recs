import React from 'react';
import { ChevronRight } from 'lucide-react';
import '../style/profile.scss';
import Navbar from '../components/navbar'; // Assuming your Navbar component path

const Profile = () => {
  // Placeholder data
  const user = {
    firstName: "FIRSTNAME",
    lastName: "LASTNAME",
    username: "Username",
    memberSince: "Day Month, Year",
    currentRead: null,
    progress: 30,
    booksRead: Array(5).fill(null), 
    toReadShelf: Array(3).fill(null) 
  };

  return (
    <>
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-picture"></div>
          <div className="profile-info">
            <h1 className="profile-name">{user.firstName} {user.lastName}</h1>
            <p className="profile-username">{user.username}</p>
            <p className="profile-member-since">Member Since {user.memberSince}</p>
            <button className="edit-profile-button">Edit Profile</button>
          </div>
        </div>

        <div className="profile-content">
          <div className="current-read-section">
            <h2 className="section-title">CURRENT<br />READ</h2>
            <div className="current-book">
              <div className="book-cover"></div>
              <div className="progress-bar">
                <div
                  className="progress-indicator"
                  style={{ height: `${user.progress}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="books-section">
            <h2 className="section-title">Books Read</h2>
            <div className="books-grid">
              {user.booksRead.map((_, index) => (
                <div key={`read-${index}`} className="book-cover"></div>
              ))}
              <div className="more-link">
                <ChevronRight size={24} />
              </div>
            </div>
          </div>

          <div className="books-section to-read-section">
            <h2 className="section-title">To-Read Shelf</h2>
            <div className="books-grid">
              {user.toReadShelf.map((_, index) => (
                <div key={`to-read-${index}`} className="book-cover"></div>
              ))}
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