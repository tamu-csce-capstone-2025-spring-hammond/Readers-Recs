// import React from 'react';
// import Navbar from '../components/navbar';
// import "../style/style.css";

// const Profile = () => {
//     return (
//     <div>
//         <div className='profile-view'>
//             {/* Top Section */}
//             <div className='profile-top-section'>
//                 <div className='profile-picture'>
//                     <img src='https://via.placeholder.com/150' alt='Profile Picture' />
//                 </div>
//                 <div className='profile-info'>
//                     <h1 id='first-last'>FirstName LastName</h1>
//                     <h2 id='username'>Username</h2>
//                     <h3>Member Since <div id='user-date'>Day Month, Year</div></h3>
//                     <button className='text-button'>Edit Profile</button>
//                 </div>
//             </div>
//             {/* Bottom Section */}
//             <div className='profile-bottom-section'>
//                 <div className='profile-bottom-left-section'>
//                     <h1>Current Read</h1>
//                     <div className='book-cover'></div>
//                     <div className='progress-bar'></div>
//                 </div>
//                 <div className='profile-bottom-right-section'>
//                     <div className='books-read-view'>
//                         <h2>Books Read</h2>
//                         <div className='books-read-scroll-area'>
//                             {/* Vector/List of Books Read GO HERE */}
//                         </div>
//                         <button className='round-button'>→</button>
//                     </div>
//                     <div className='to-read-view'>
//                         <h2>To-Read Shelf</h2>
//                         <div className='to-read-scroll-area'>
//                             {/* Vector/List of To-Read Covers GO HERE */}
//                         </div>
//                         <button className='round-button'>→</button>
//                     </div>
//                 </div>
//             </div>
//         </div>
//         <Navbar /> {}
//     </div>
//     );
// };

// export default Profile;

// import React from 'react';
// import { ChevronRight } from 'lucide-react';
// import '../style/profile.scss';

// const Profile = () => {
//   // Placeholder data
//   const user = {
//     firstName: "FIRSTNAME",
//     lastName: "LASTNAME",
//     username: "Username",
//     memberSince: "Day Month, Year",
//     currentRead: null,
//     progress: 30, // Example progress percentage
//     booksRead: Array(6).fill(null),
//     toReadShelf: Array(3).fill(null)
//   };

//   return (
//     <div className="profile-container">
//       <div className="profile-header">
//         <div className="profile-picture"></div>
//         <div className="profile-info">
//           <h1 className="profile-name">{user.firstName} {user.lastName}</h1>
//           <p className="profile-username">{user.username}</p>
//           <p className="profile-member-since">Member Since {user.memberSince}</p>
//           <button className="edit-profile-button">Edit Profile</button>
//         </div>
//       </div>

//       <div className="profile-content">
//         <div className="current-read-section">
//           <h2 className="section-title">CURRENT READ</h2>
//           <div className="current-book">
//             <div className="book-cover"></div>
//             <div className="progress-bar">
//               <div 
//                 className="progress-indicator" 
//                 style={{ height: `${user.progress}%` }}
//               ></div>
//             </div>
//           </div>
//         </div>

//         <div className="books-section">
//           <h2 className="section-title">Books Read</h2>
//           <div className="books-grid">
//             {user.booksRead.map((_, index) => (
//               <div key={`read-${index}`} className="book-cover"></div>
//             ))}
//             {/* <Link to="/books-read" className="more-link">
//               <ChevronRight size={24} />
//             </Link> */}
//           </div>
//         </div>

//         <div className="books-section">
//           <h2 className="section-title">To-Read Shelf</h2>
//           <div className="books-grid">
//             {user.toReadShelf.map((_, index) => (
//               <div key={`to-read-${index}`} className="book-cover"></div>
//             ))}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Profile;




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
    progress: 30, // Example progress percentage
    booksRead: Array(5).fill(null), // Changed to 5 to match image
    toReadShelf: Array(6).fill(null) // Adjusted to match image
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