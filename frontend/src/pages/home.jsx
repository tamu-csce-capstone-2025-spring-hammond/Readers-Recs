// import React from 'react';
// import Navbar from '../components/navbar';
// import "../style/style.css";

// const Home = () => {
//     return (
//     <div>
//         {/* Top Section (Book Recommendations) */}
//         <div className='book-recommendation-view'>
//             <h1>Book RECOMMENDATIONS</h1>
//             <div className='book-recommendation-covers'>
//                 {/* Spots for 5 Book Covers Recommended GO HERE */}
//                 <div className='book-cover'></div>
//                 <div className='book-cover'></div>
//                 <div className='book-cover'></div>
//                 <div className='book-cover'></div>
//                 <div className='book-cover'></div>
//             </div>
//         </div>
//         {/* Bottom Section (Current Read, Last Finished, To-Read) */}
//         <div className='home-bottom-section'>
//             {/* Current Read */}
//             <div className='current-read-view'>
//                 <h1>Current Read</h1>
//                 <div className='book-cover'></div>
//                 <button className='text-button'>Update Progress</button>
//             </div>
//             {/* Last Finished */}
//             <div className='last-finished-view'>
//                 <h1>Last Finished</h1>
//                 <div className='book-cover'></div>
//                 <button className='text-button'>Go to Chat→</button>
//             </div>
//             {/* To-Read Shelf*/}
//             <div className='to-read-view'>
//                 <h1>To-Read Shelf</h1>
//                 <div className='to-read-scroll-area'>
//                     {/* Vector/List of To-Read Covers GO HERE */}
//                 </div>
//                 <button className='round-button'>→</button>
//             </div>
//         </div>
//         <Navbar /> {}
//     </div>
//     );
// };

// export default Home;


import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import Navbar from '../components/navbar'; 
import '../style/home.scss';

const Home = () => {
  const recommendations = Array(6).fill(null);
  const toReadShelf = Array(3).fill(null);

  return (
    <>
      {/* <Navbar />  */}
      <div className="home-container">
        <div className="recommendations-section">
          <h1 className="section-title">Book RECOMMENDATIONS</h1>
          <div className="book-grid">
            {recommendations.map((_, index) => (
              <div key={`rec-${index}`} className="book-cover"></div>
            ))}
          </div>
        </div>

        <div className="reading-sections">
          <div className="reading-section">
            <h2 className="section-title">CURRENT READ</h2>
            <div className="current-book">
              <div className="book-cover"></div>
              <button className="update-button">Update Progress</button>
            </div>
          </div>

          <div className="reading-section">
            <h2 className="section-title">LAST FINISHED</h2>
            <div className="last-finished">
              <div className="book-cover"></div>
              <Link to="/chats" className="chat-button">
                Go to chat room <ChevronRight size={16} />
              </Link>
            </div>
          </div>

          <div className="reading-section to-read">
            <h2 className="section-title">TO-READ SHELF</h2>
            <div className="book-grid">
              {toReadShelf.map((_, index) => (
                <div key={`to-read-${index}`} className="book-cover"></div>
              ))}
              <Link to="/search" className="more-link">
                <ChevronRight size={44} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    <Navbar /> 
    </>
  );
};

export default Home;
