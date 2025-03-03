import React from 'react';
import Navbar from '../components/navbar';
import "../style/style.css";

const Profile = () => {
    return (
    <div>
        <div className='profile-view'>
            {/* Top Section */}
            <div className='profile-top-section'>
                <div className='profile-picture'>
                    <img src='https://via.placeholder.com/150' alt='Profile Picture' />
                </div>
                <div className='profile-info'>
                    <h1 id='first-last'>FirstName LastName</h1>
                    <h2 id='username'>Username</h2>
                    <h3>Member Since <div id='user-date'>Day Month, Year</div></h3>
                    <button className='text-button'>Edit Profile</button>
                </div>
            </div>
            {/* Bottom Section */}
            <div className='profile-bottom-section'>
                <div className='profile-bottom-left-section'>
                    <h1>Current Read</h1>
                    <div className='book-cover'></div>
                    <div className='progress-bar'></div>
                </div>
                <div className='profile-bottom-right-section'>
                    <div className='books-read-view'>
                        <h2>Books Read</h2>
                        <div className='books-read-scroll-area'>
                            {/* Vector/List of Books Read GO HERE */}
                        </div>
                        <button className='round-button'>→</button>
                    </div>
                    <div className='to-read-view'>
                        <h2>To-Read Shelf</h2>
                        <div className='to-read-scroll-area'>
                            {/* Vector/List of To-Read Covers GO HERE */}
                        </div>
                        <button className='round-button'>→</button>
                    </div>
                </div>
            </div>
        </div>
        <Navbar /> {}
    </div>
    );
};

export default Profile;