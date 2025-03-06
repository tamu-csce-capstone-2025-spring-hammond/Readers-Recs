// import React from 'react';
// import { Link } from 'react-router-dom';
// import { ChevronRight } from 'lucide-react';
// import Navbar from '../components/navbar'; 
// import '../style/home.scss';

// const Home = () => {
//   const recommendations = Array(6).fill(null);
//   const toReadShelf = Array(3).fill(null);

//   return (
//     <>
//       {/* <Navbar />  */}
//       <div className="home-container">
//         <div className="recommendations-section">
//           <h1 className="section-title">Book RECOMMENDATIONS</h1>
//           <div className="book-grid">
//             {recommendations.map((_, index) => (
//               <div key={`rec-${index}`} className="book-cover"></div>
//             ))}
//           </div>
//         </div>

//         <div className="reading-sections">
//           <div className="reading-section">
//             <h2 className="section-title">CURRENT READ</h2>
//             <div className="current-book">
//               <div className="book-cover"></div>
//               <button className="update-button">Update Progress</button>
//             </div>
//           </div>

//           <div className="reading-section">
//             <h2 className="section-title">LAST FINISHED</h2>
//             <div className="last-finished">
//               <div className="book-cover"></div>
//               <Link to="/chats" className="chat-button">
//                 Go to chat room <ChevronRight size={16} />
//               </Link>
//             </div>
//           </div>

//           <div className="reading-section to-read">
//             <h2 className="section-title">TO-READ SHELF</h2>
//             <div className="book-grid">
//               {toReadShelf.map((_, index) => (
//                 <div key={`to-read-${index}`} className="book-cover"></div>
//               ))}
//               <Link to="/search" className="more-link">
//                 <ChevronRight size={44} />
//               </Link>
//             </div>
//           </div>
//         </div>
//       </div>
//     <Navbar /> 
//     </>
//   );
// };

// export default Home;


// i liek it but too much scrolling

// import React, { useState, useEffect } from 'react';
// import { Link } from 'react-router-dom';
// import { ChevronRight, BookOpen, Clock, Award, PlusCircle, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
// import Navbar from '../components/navbar'; 
// import '../style/home.scss';

// const Home = () => {
//   const [isLoaded, setIsLoaded] = useState(false);
//   const [activeSection, setActiveSection] = useState(null);
  
//   // Sample data - replace with your actual data
//   const recommendations = Array(6).fill(null).map((_, i) => ({
//     id: i,
//     title: `Book ${i+1}`,
//     author: `Author ${i+1}`,
//     coverColor: `hsl(${i * 60}, 70%, 80%)` // Just for demo
//   }));
  
//   const toReadShelf = Array(3).fill(null).map((_, i) => ({
//     id: i,
//     title: `To Read ${i+1}`,
//     author: `Author ${i+1}`,
//     coverColor: `hsl(${i * 40 + 120}, 70%, 75%)` // Just for demo
//   }));

//   const currentBook = {
//     title: "Current Reading",
//     author: "Author Name",
//     progress: 67,
//     coverColor: "hsl(200, 70%, 80%)"
//   };

//   const lastFinishedBook = {
//     title: "Last Finished",
//     author: "Author Name",
//     rating: "thumbsUp", // Changed from numeric to thumbs rating
//     coverColor: "hsl(320, 70%, 80%)"
//   };

//   // Animate elements on page load
//   useEffect(() => {
//     setIsLoaded(true);
//   }, []);

//   // Handle hover effects for sections
//   const handleSectionHover = (section) => {
//     setActiveSection(section);
//   };

//   return (
//     <div className={`page-wrapper ${isLoaded ? 'loaded' : ''}`}>
//       <div className="home-container">
//         <div className="page-header">
//           <h1 className="page-title">Reader's Corner</h1>
//           <p className="welcome-text">Track, discover, and enjoy your books</p>
//         </div>
      
//         <div 
//           className="recommendations-section"
//           onMouseEnter={() => handleSectionHover('recommendations')}
//           onMouseLeave={() => handleSectionHover(null)}
//         >
//           <div className="section-header">
//             <BookOpen className="section-icon" size={18} />
//             <h2 className="section-title">Recommended For You</h2>
//           </div>
          
//           <div className="book-cards-container">
//             <div className="book-grid recommendations-grid">
//               {recommendations.map((book, index) => (
//                 <div 
//                   key={`rec-${index}`} 
//                   className="book-card"
//                   style={{
//                     animationDelay: `${0.1 + index * 0.03}s` // Faster animation delay
//                   }}
//                 >
//                   <div 
//                     className="book-cover" 
//                     style={{ backgroundColor: book.coverColor }}
//                   >
//                     <div className="book-spine"></div>
//                   </div>
//                   <div className="book-info">
//                     <h3 className="book-title">{book.title}</h3>
//                     <p className="book-author">{book.author}</p>
//                   </div>
//                 </div>
//               ))}
//             </div>
//           </div>
//         </div>

//         <div className="reading-sections">
//           <div 
//             className={`reading-section current-section ${activeSection === 'current' ? 'active' : ''}`}
//             onMouseEnter={() => handleSectionHover('current')}
//             onMouseLeave={() => handleSectionHover(null)}
//           >
//             <div className="section-header">
//               <Clock className="section-icon" size={18} />
//               <h2 className="section-title">Currently Reading</h2>
//             </div>
            
//             <div className="current-book">
//               <div 
//                 className="book-cover featured-cover" 
//                 style={{ backgroundColor: currentBook.coverColor }}
//               >
//                 <div className="book-spine"></div>
//                 <div className="reading-progress-container">
//                   <div 
//                     className="reading-progress-bar" 
//                     style={{ width: `${currentBook.progress}%` }}
//                   ></div>
//                 </div>
//               </div>
//               <div className="book-info">
//                 <h3 className="book-title">{currentBook.title}</h3>
//                 <p className="book-author">{currentBook.author}</p>
//                 <div className="progress-info">
//                   <span className="progress-percentage">{currentBook.progress}%</span>
//                   <span className="progress-text">completed</span>
//                 </div>
//               </div>
//               <button className="action-button update-button">
//                 Update Progress
//               </button>
//             </div>
//           </div>

//           <div 
//             className={`reading-section finished-section ${activeSection === 'finished' ? 'active' : ''}`}
//             onMouseEnter={() => handleSectionHover('finished')}
//             onMouseLeave={() => handleSectionHover(null)}
//           >
//             <div className="section-header">
//               <Award className="section-icon" size={18} />
//               <h2 className="section-title">Last Finished</h2>
//             </div>
            
//             <div className="last-finished">
//               <div 
//                 className="book-cover featured-cover" 
//                 style={{ backgroundColor: lastFinishedBook.coverColor }}
//               >
//                 <div className="book-spine"></div>
//                 <div className="book-badge">
//                   <span>Finished</span>
//                 </div>
//               </div>
//               <div className="book-info">
//                 <h3 className="book-title">{lastFinishedBook.title}</h3>
//                 <p className="book-author">{lastFinishedBook.author}</p>
                
//                 {/* New thumbs rating system */}
//                 <div className="rating-thumbs">
//                   <button 
//                     className={`thumb-btn thumbs-up ${lastFinishedBook.rating === 'thumbsUp' ? 'selected' : ''}`}
//                   >
//                     <ThumbsUp size={22} />
//                     <span>Loved it</span>
//                   </button>
                  
//                   <button 
//                     className={`thumb-btn thumbs-mid ${lastFinishedBook.rating === 'thumbsMid' ? 'selected' : ''}`}
//                   >
//                     <Minus size={22} />
//                     <span>It's okay</span>
//                   </button>
                  
//                   <button 
//                     className={`thumb-btn thumbs-down ${lastFinishedBook.rating === 'thumbsDown' ? 'selected' : ''}`}
//                   >
//                     <ThumbsDown size={22} />
//                     <span>Not great</span>
//                   </button>
//                 </div>
//               </div>
//               <Link to="/chats" className="action-button chat-button">
//                 <span>Discuss Book</span>
//                 <ChevronRight size={14} />
//               </Link>
//             </div>
//           </div>

//           <div 
//             className={`reading-section to-read-section ${activeSection === 'toread' ? 'active' : ''}`}
//             onMouseEnter={() => handleSectionHover('toread')}
//             onMouseLeave={() => handleSectionHover(null)}
//           >
//             <div className="section-header">
//               <PlusCircle className="section-icon" size={18} />
//               <h2 className="section-title">Reading Wishlist</h2>
//             </div>
            
//             <div className="to-read-shelf">
//               <div className="book-grid to-read-grid">
//                 {toReadShelf.map((book, index) => (
//                   <div 
//                     key={`to-read-${index}`} 
//                     className="book-card wishlist-book"
//                     style={{
//                       animationDelay: `${0.1 + index * 0.03}s` // Faster animation delay
//                     }}
//                   >
//                     <div 
//                       className="book-cover" 
//                       style={{ backgroundColor: book.coverColor }}
//                     >
//                       <div className="book-spine"></div>
//                     </div>
//                     <div className="book-info">
//                       <h3 className="book-title">{book.title}</h3>
//                       <p className="book-author">{book.author}</p>
//                     </div>
//                   </div>
//                 ))}
//                 <Link to="/search" className="add-more-card">
//                   <div className="add-more-content">
//                     <PlusCircle size={24} />
//                     <span>Find More</span>
//                   </div>
//                 </Link>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//       <Navbar />
//     </div>
//   );
// };

// export default Home;


import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, BookOpen, Clock, Award, PlusCircle, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import Navbar from '../components/navbar'; 
import '../style/home.scss';
import UpdateProgress from '../components/updateprogress';

const Home = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [activeSection, setActiveSection] = useState(null);
  const [showUpdateProgress, setShowUpdateProgress] = useState(false);
  const [bookProgress, setBookProgress] = useState(67);
  
  // Sample data - replace with your actual data
  const recommendations = Array(6).fill(null).map((_, i) => ({
    id: i,
    title: `Book ${i+1}`,
    author: `Author ${i+1}`,
    coverColor: `hsl(${i * 60}, 70%, 80%)` // Just for demo
  }));
  
  const toReadShelf = Array(3).fill(null).map((_, i) => ({
    id: i,
    title: `To Read ${i+1}`,
    author: `Author ${i+1}`,
    coverColor: `hsl(${i * 40 + 120}, 70%, 75%)` // Just for demo
  }));

  const currentBook = {
    title: "Current Reading",
    author: "Author Name",
    progress: 67,
    coverColor: "hsl(200, 70%, 80%)"
  };

  const lastFinishedBook = {
    title: "Last Finished",
    author: "Author Name",
    rating: "thumbsUp", // Changed from numeric to thumbs rating
    coverColor: "hsl(320, 70%, 80%)"
  };

  // Animate elements on page load
  useEffect(() => {
    setIsLoaded(true);
  }, []);

  // Handle hover effects for sections
  const handleSectionHover = (section) => {
    setActiveSection(section);
  };

  const handleUpdateClick = () => {
    setShowUpdateProgress(true);
  };

  const handleProgressUpdate = (newProgress) => {
    setBookProgress(newProgress);
    setShowUpdateProgress(false);
  };

  return (
    <div className={`page-wrapper ${isLoaded ? 'loaded' : ''}`}>
      <div className="home-container">
        <div className="page-header">
          <h1 className="page-title">My Corner</h1>
          <p className="welcome-text">Track, discover, and enjoy your books</p>
        </div>
        
        <div className="main-grid">
          {/* First Row - Currently Reading and Last Finished */}
          <div className="top-row">
            <div 
              className={`reading-section current-section ${activeSection === 'current' ? 'active' : ''}`}
              onMouseEnter={() => handleSectionHover('current')}
              onMouseLeave={() => handleSectionHover(null)}
            >
              <div className="section-header">
                <Clock className="section-icon" size={32} />
                <h2 className="section-title">Currently Reading</h2>
              </div>
              
              <div className="current-book">
                <div className="book-display">
                  <div 
                    className="book-cover featured-cover" 
                    style={{ backgroundColor: currentBook.coverColor }}
                  >
                    <div className="book-spine"></div>
                    <div className="reading-progress-container">
                      <div 
                        className="reading-progress-bar" 
                        style={{ width: `${currentBook.progress}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="book-info">
                    <h3 className="book-title">{currentBook.title}</h3>
                    <p className="book-author">{currentBook.author}</p>
                    <div className="progress-info">
                      <span className="progress-percentage">{currentBook.progress}%</span>
                      <span className="progress-text">completed</span>
                    </div>
                    <button className="action-button update-button" onClick={handleUpdateClick}>
                      Update Progress
                    </button>
                  </div>
                </div>
              </div>
            </div>
            {showUpdateProgress && (
              <UpdateProgress currentProgress={bookProgress} onUpdate={handleProgressUpdate} />
            )}
            <div 
              className={`reading-section finished-section ${activeSection === 'finished' ? 'active' : ''}`}
              onMouseEnter={() => handleSectionHover('finished')}
              onMouseLeave={() => handleSectionHover(null)}
            >
              <div className="section-header">
                <Award className="section-icon" size={32} />
                <h2 className="section-title">Last Finished</h2>
              </div>
              
              <div className="last-finished">
                <div className="book-display">
                  <div 
                    className="book-cover featured-cover" 
                    style={{ backgroundColor: lastFinishedBook.coverColor }}
                  >
                    <div className="book-spine"></div>
                    <div className="book-badge">
                      <span>Finished</span>
                    </div>
                  </div>
                  <div className="book-info">
                    <h3 className="book-title">{lastFinishedBook.title}</h3>
                    <p className="book-author">{lastFinishedBook.author}</p>
                    
                    {/* Thumbs rating system */}
                    <div className="rating-thumbs">
                      <button 
                        className={`thumb-btn thumbs-up ${lastFinishedBook.rating === 'thumbsUp' ? 'selected' : ''}`}
                      >
                        <ThumbsUp size={20} />
                        <span>Loved it</span>
                      </button>
                      
                      <button 
                        className={`thumb-btn thumbs-mid ${lastFinishedBook.rating === 'thumbsMid' ? 'selected' : ''}`}
                      >
                        <Minus size={20} />
                        <span>It's okay</span>
                      </button>
                      
                      <button 
                        className={`thumb-btn thumbs-down ${lastFinishedBook.rating === 'thumbsDown' ? 'selected' : ''}`}
                      >
                        <ThumbsDown size={20} />
                        <span>Not great</span>
                      </button>
                    </div>
                    <Link to="/chats" className="action-button chat-button">
                      <span>Discuss Book</span>
                      <ChevronRight size={14} />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Second Row - Recommendations and Reading Wishlist */}
          <div className="bottom-row">
            <div 
              className="recommendations-section"
              onMouseEnter={() => handleSectionHover('recommendations')}
              onMouseLeave={() => handleSectionHover(null)}
            >
              <div className="section-header">
                <BookOpen className="section-icon" size={32} />
                <h2 className="section-title">Recommended For You</h2>
              </div>
              
              <div className="book-cards-container">
                <div className="book-grid recommendations-grid">
                  {recommendations.map((book, index) => (
                    <div 
                      key={`rec-${index}`} 
                      className="book-card"
                      style={{
                        animationDelay: `${0.1 + index * 0.03}s`
                      }}
                    >
                      <div 
                        className="book-cover" 
                        style={{ backgroundColor: book.coverColor }}
                      >
                        <div className="book-spine"></div>
                      </div>
                      <div className="book-info">
                        <h3 className="book-title">{book.title}</h3>
                        <p className="book-author">{book.author}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div 
              className={`reading-section to-read-section ${activeSection === 'toread' ? 'active' : ''}`}
              onMouseEnter={() => handleSectionHover('toread')}
              onMouseLeave={() => handleSectionHover(null)}
            >
              <div className="section-header">
                <PlusCircle className="section-icon" size={32} />
                <h2 className="section-title">Reading Wishlist</h2>
              </div>
              
              <div className="to-read-shelf">
                <div className="book-grid to-read-grid">
                  {toReadShelf.map((book, index) => (
                    <div 
                      key={`to-read-${index}`} 
                      className="book-card wishlist-book"
                      style={{
                        animationDelay: `${0.1 + index * 0.03}s`
                      }}
                    >
                      <div 
                        className="book-cover" 
                        style={{ backgroundColor: book.coverColor }}
                      >
                        <div className="book-spine"></div>
                      </div>
                      <div className="book-info">
                        <h3 className="book-title">{book.title}</h3>
                        <p className="book-author">{book.author}</p>
                      </div>
                    </div>
                  ))}
                  <Link to="/search" className="add-more-card">
                    <div className="add-more-content">
                      <PlusCircle size={24} />
                      <span>Find More</span>
                    </div>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Navbar />
    </div>
  );
};

export default Home;