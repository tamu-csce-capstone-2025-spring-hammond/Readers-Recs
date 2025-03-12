import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';
import Navbar from '../components/navbar'; 
import '../style/style.css';

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
