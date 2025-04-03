import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, BookOpen, Clock, Award, PlusCircle, ThumbsUp, ThumbsDown, Minus } from 'lucide-react';
import Navbar from '../components/navbar';
import '../style/style.css';
import UpdateProgress from '../components/updateprogress';
import { ClipLoader } from "react-spinners";


const Home = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [activeSection, setActiveSection] = useState(null);
  const [showUpdateProgress, setShowUpdateProgress] = useState(false);
  const [bookProgress, setBookProgress] = useState(0);
  const [user, setUser] = useState(null);
  const [bookshelf, setBookshelf] = useState({
    currentRead: null,
    lastRead: null,
    toReadShelf: [],
  });
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(true);
  const [loadingBookshelf, setLoadingBookshelf] = useState(true);

  
  // // Sample data - replace with your actual data
  // const recommendations = Array(6).fill(null).map((_, i) => ({
  //   id: i,
  //   title: `Book ${i+1}`,
  //   author: `Author ${i+1}`,
  //   coverColor: `hsl(${i * 60}, 70%, 80%)` // Just for demo
  // }));
  
  // const toReadShelf = Array(3).fill(null).map((_, i) => ({
  //   id: i,
  //   title: `To Read ${i+1}`,
  //   author: `Author ${i+1}`,
  //   coverColor: `hsl(${i * 40 + 120}, 70%, 75%)` // Just for demo
  // }));

  // const currentBook = {
  //   title: "Current Reading",
  //   author: "Author Name",
  //   progress: bookProgress,
  //   coverColor: "#ffffff"
  // };

  // const [lastFinishedBook, setLastFinishedBook] = useState({
  //   title: "Last Finished",
  //   author: "Author Name",
  //   rating: "thumbsMid", // Changed from numeric to thumbs rating
  //   coverColor: "#ffffff"
  // });

  // Animate elements on page load
  useEffect(() => {
    setIsLoaded(true);
    const fetchUserProfile = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No token found');
        // setLoading(false);
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
        fetchRecommendations(profileData.id);  
      } catch (error) {
        console.error('Error fetching profile or bookshelf data:', error);
      } finally {
        // setLoading(false);
      }
    };

    const fetchBookshelfData = async (userId, token) => {
      setLoadingBookshelf(true);

      try {
        const endpoints = [
          { key: 'currentRead', url: `books/currently-reading` },
          { key: 'lastRead', url: `books/lastread` },
          { key: 'toReadShelf', url: `books/to-read` },
        ];
        
        for (const { key, url } of endpoints) {
          const response = await fetch(`http://localhost:8000/shelf/api/user/${userId}/${url}`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
    
          if (response.ok) {
            const data = await response.json();
            
            // Fetch current page number if it's the current read
            if (key === "currentRead" && data) {
              const pageResponse = await fetch(`http://localhost:8000/shelf/api/user/${userId}/bookshelf/${data._id}/current-page`);
              if (pageResponse.ok) {
                const pageData = await pageResponse.json();
                // console.log("current page:", pageData.page_number)

                data.current_page = pageData.page_number; // Attach page info
                // progress = data.current_page / data.page_count
                console.log("book progress:", (data.current_page / data.page_count))
                setBookProgress(Math.round((data.current_page / data.page_count) * 100))
              }
            }
            
            setBookshelf((prev) => ({ ...prev, [key]: data }));
          }
        }
      } catch (error) {
        console.error('Error fetching bookshelf data:', error);
      } finally {
        setLoadingBookshelf(false);
      }
    };
    

    const fetchRecommendations = async (userId) => {
      setLoadingRecommendations(true);

      try {
        console.log("Fetching recs");
        console.log("from http://localhost:8000/recs/api/user/${userId}/recommendations ");
        const response = await fetch(`http://localhost:8000/recs/api/user/${userId}/recommendations`);
        
        if (!response.ok) throw new Error('Failed to fetch recommendations');
        const data = await response.json();
        console.log("recs:", data.recommendations)
        setRecommendations(data.recommendations);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setLoadingRecommendations(false);
      }
    };
  


    fetchUserProfile();
  }, []);

  const handleSectionHover = (section) => {
    setActiveSection(section);
  };

  const handleUpdateClick = () => {
    setShowUpdateProgress(true);
  };

  const handleProgressUpdate = async (newProgress) => {
    if (!bookshelf.currentRead) return;
  
    const userId = user?.id;
    const bookId = bookshelf.currentRead._id;
    const totalPages = bookshelf.currentRead.page_count;
  
    const newPageNumber = Math.round((newProgress / 100) * totalPages);
  
    try {
      const response = await fetch(`http://localhost:8000/shelf/api/user/${userId}/bookshelf/${bookId}/current-page`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ page_number: newPageNumber }),
      });
  
      if (!response.ok) throw new Error('Failed to update progress');
  
      setBookProgress(newProgress);
      setBookshelf((prev) => ({
        ...prev,
        currentRead: { ...prev.currentRead, current_page: newPageNumber },
      }));
  
    } catch (error) {
      console.error('Error updating progress:', error);
    } finally {
      setShowUpdateProgress(false);
    }
  };

  const handleRatingClick = async (newRating) => {
    if (!user || !bookshelf.lastRead) return;
    
    const userId = user.id;
    const bookId = bookshelf.lastRead._id;

    setBookshelf((prev) => ({
      ...prev,
      lastRead: { ...prev.lastRead, rating: newRating },
    }));
  
  
    try {
      const response = await fetch(`http://localhost:8000/shelf/api/user/${userId}/bookshelf/${bookId}/rating`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ rating: newRating }),
      });
  
      if (!response.ok) throw new Error("Failed to update rating");
  
      
    } catch (error) {
      console.error("Error updating book rating:", error);
    }
  };
  
  if (loadingRecommendations || loadingBookshelf) {
    return (
      <div className={`page-wrapper ${isLoaded ? 'loaded' : ''}`}>
      <div className="home-container">
        <div className="main-grid">
          
          {/* Left side - Recommended For You */}
          <div className="left-column">
            <div
              className="recommendations-section"
              onMouseEnter={() => handleSectionHover('recommendations')}
              onMouseLeave={() => handleSectionHover(null)}
            >
              <div className="section-header">
                <BookOpen className="section-icon" size={32} />
                <h2 className="section-title">Recommended For You</h2>
                <button className="refresh-btn">↻</button>
                <div className="flex items-center justify-center mt-4">
                <ClipLoader color="black" loading={loadingRecommendations || loadingBookshelf} size={50} />
                </div>
            </div>
          </div>
          </div>
  
          {/* Right side - Currently Reading and Last Finished */}
          <div className="right-column">
            <div className="right-top">
              
              {/* Currently Reading */}
              <div className="reading-section current-section">
                <div className="section-header">
                  <Clock className="section-icon" size={32} />
                  <h2 className="section-title">Currently Reading</h2>
                </div>
                <div className="current-book">
                  {loadingBookshelf ? (
                    <p>Loading currently reading book...</p>
                  ) : bookshelf.currentRead ? (
                    <div className="book-display">
                      <div
                        className="home-book-cover featured-cover"
                        style={{ backgroundImage: `url(${bookshelf.currentRead.cover_image ?? ''})` }}
                      >
                        <div className="reading-progress-container">
                          <div className="reading-progress-bar" style={{ width: `${bookProgress}%` }}></div>
                        </div>
                      </div>
                      <div className="book-info">
                        <h3 className="book-title">{bookshelf.currentRead.title}</h3>
                        <p className="book-author">{bookshelf.currentRead.author?.[0] ?? 'Unknown author'}</p>
                        <div className="progress-info">
                          <span className="progress-percentage">{bookProgress}%</span>
                          <span className="progress-text">completed</span>
                        </div>
                        <button className="action-button update-button" onClick={handleUpdateClick}>
                          Update Progress
                        </button>
                      </div>
                      {showUpdateProgress && (
                        <UpdateProgress
                          currentPage={bookshelf.currentRead?.current_page || 0}
                          totalPages={bookshelf.currentRead?.page_count || 1}
                          onUpdate={handleProgressUpdate}
                        />
                      )}
                    </div>
                  ) : (
                    <p>No book currently being read.</p>
                  )}
                </div>
              </div>
  
              {/* Last Finished */}
              <div className="reading-section finished-section">
                <div className="section-header">
                  <Award className="section-icon" size={32} />
                  <h2 className="section-title">Last Finished</h2>
                </div>
                <div className="last-finished">
                  {loadingBookshelf ? (
                    <p>Loading last finished book...</p>
                  ) : bookshelf.lastRead ? (
                    <div className="book-display">
                      <div
                        className="home-book-cover featured-cover"
                        style={{ backgroundImage: `url(${bookshelf.lastRead.cover_image ?? ''})` }}
                      >
                        <div className="book-badge">
                          <span>Finished</span>
                        </div>
                      </div>
                      <div className="book-info">
                        <h3 className="book-title">{bookshelf.lastRead.title}</h3>
                        <p className="book-author">{bookshelf.lastRead.author?.[0] ?? 'Unknown author'}</p>
                        <div className="rating-thumbs">
                          <button
                            className={`thumb-btn thumbs-up ${bookshelf.lastRead?.rating === 'pos' ? 'selected' : ''}`}
                            onClick={() => handleRatingClick('pos')}
                          >
                            <ThumbsUp size={20} />
                            <span>Loved it</span>
                          </button>
                          <button
                            className={`thumb-btn thumbs-mid ${bookshelf.lastRead?.rating === 'mid' ? 'selected' : ''}`}
                            onClick={() => handleRatingClick('mid')}
                          >
                            <Minus size={20} />
                            <span>It's okay</span>
                          </button>
                          <button
                            className={`thumb-btn thumbs-down ${bookshelf.lastRead?.rating === 'neg' ? 'selected' : ''}`}
                            onClick={() => handleRatingClick('neg')}
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
                  ) : (
                    <p>No books finished.</p>
                  )}
                </div>
              </div>
            </div>
  
            {/* Reading Wishlist */}
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
                {loadingBookshelf ? (
                  <p>Loading reading wishlist...</p>
                ) : (
                  <div className="book-grid to-read-grid">
                    {bookshelf.toReadShelf.map((book, index) => (
                      <div
                        key={`to-read-${index}`}
                        className="wishlist-book"
                        style={{ animationDelay: `${0.1 + index * 0.03}s` }}
                      >
                        <div
                          className="home-book-cover"
                          style={{ backgroundImage: `url(${book.cover_image ?? ''})` }}
                        ></div>
                      </div>
                    ))}
                    <Link to="/search" className="add-more-card">
                      <div className="add-more-content">
                        <PlusCircle size={24} />
                        <span>Find More</span>
                      </div>
                    </Link>
                  </div>
                )}
              </div>
            </div>
  
          </div>
        </div>
      </div>
      <Navbar />
    </div>
  );
}


  return (
    <div className={`page-wrapper ${isLoaded ? 'loaded' : ''}`}>
      <div className="home-container">
        <div className="main-grid">
          
          {/* Left side - Recommended For You */}
          <div className="left-column">
            <div
              className="recommendations-section"
              onMouseEnter={() => handleSectionHover('recommendations')}
              onMouseLeave={() => handleSectionHover(null)}
            >
              <div className="section-header">
                <BookOpen className="section-icon" size={32} />
                <h2 className="section-title">Recommended For You</h2>
                <button className="refresh-btn">↻</button>
              </div>
              <div className="book-cards-container">
                {loadingRecommendations ? (
                  <p>Loading recommendations...</p>
                ) : recommendations.length > 0 ? (
                  recommendations.map((book) => (
                    <div key={book.id} className="book-card">
                      <div
                        className="home-book-cover"
                        style={{ backgroundImage: `url(${book.cover_image ?? ''})` }}
                      ></div>
                      <div className="book-info">
                        <h3 className="book-title">{book.title}</h3>
                        <p className="book-author">{book.author}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p>No recommendations available.</p>
                )}
              </div>
            </div>
          </div>
  
          {/* Right side - Currently Reading and Last Finished */}
          <div className="right-column">
            <div className="right-top">
              
              {/* Currently Reading */}
              <div className="reading-section current-section">
                <div className="section-header">
                  <Clock className="section-icon" size={32} />
                  <h2 className="section-title">Currently Reading</h2>
                </div>
                <div className="current-book">
                  {loadingBookshelf ? (
                    <p>Loading currently reading book...</p>
                  ) : bookshelf.currentRead ? (
                    <div className="book-display">
                      <div
                        className="home-book-cover featured-cover"
                        style={{ backgroundImage: `url(${bookshelf.currentRead.cover_image ?? ''})` }}
                      >
                        <div className="reading-progress-container">
                          <div className="reading-progress-bar" style={{ width: `${bookProgress}%` }}></div>
                        </div>
                      </div>
                      <div className="book-info">
                        <h3 className="book-title">{bookshelf.currentRead.title}</h3>
                        <p className="book-author">{bookshelf.currentRead.author?.[0] ?? 'Unknown author'}</p>
                        <div className="progress-info">
                          <span className="progress-percentage">{bookProgress}%</span>
                          <span className="progress-text">completed</span>
                        </div>
                        <button className="action-button update-button" onClick={handleUpdateClick}>
                          Update Progress
                        </button>
                      </div>
                      {showUpdateProgress && (
                        <UpdateProgress
                          currentPage={bookshelf.currentRead?.current_page || 0}
                          totalPages={bookshelf.currentRead?.page_count || 1}
                          onUpdate={handleProgressUpdate}
                        />
                      )}
                    </div>
                  ) : (
                    <p>No book currently being read.</p>
                  )}
                </div>
              </div>
  
              {/* Last Finished */}
              <div className="reading-section finished-section">
                <div className="section-header">
                  <Award className="section-icon" size={32} />
                  <h2 className="section-title">Last Finished</h2>
                </div>
                <div className="last-finished">
                  {loadingBookshelf ? (
                    <p>Loading last finished book...</p>
                  ) : bookshelf.lastRead ? (
                    <div className="book-display">
                      <div
                        className="home-book-cover featured-cover"
                        style={{ backgroundImage: `url(${bookshelf.lastRead.cover_image ?? ''})` }}
                      >
                        <div className="book-badge">
                          <span>Finished</span>
                        </div>
                      </div>
                      <div className="book-info">
                        <h3 className="book-title">{bookshelf.lastRead.title}</h3>
                        <p className="book-author">{bookshelf.lastRead.author?.[0] ?? 'Unknown author'}</p>
                        <div className="rating-thumbs">
                          <button
                            className={`thumb-btn thumbs-up ${bookshelf.lastRead?.rating === 'pos' ? 'selected' : ''}`}
                            onClick={() => handleRatingClick('pos')}
                          >
                            <ThumbsUp size={20} />
                            <span>Loved it</span>
                          </button>
                          <button
                            className={`thumb-btn thumbs-mid ${bookshelf.lastRead?.rating === 'mid' ? 'selected' : ''}`}
                            onClick={() => handleRatingClick('mid')}
                          >
                            <Minus size={20} />
                            <span>It's okay</span>
                          </button>
                          <button
                            className={`thumb-btn thumbs-down ${bookshelf.lastRead?.rating === 'neg' ? 'selected' : ''}`}
                            onClick={() => handleRatingClick('neg')}
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
                  ) : (
                    <p>No books finished.</p>
                  )}
                </div>
              </div>
            </div>
  
            {/* Reading Wishlist */}
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
                {loadingBookshelf ? (
                  <p>Loading reading wishlist...</p>
                ) : (
                  <div className="book-grid to-read-grid">
                    {bookshelf.toReadShelf.map((book, index) => (
                      <div
                        key={`to-read-${index}`}
                        className="wishlist-book"
                        style={{ animationDelay: `${0.1 + index * 0.03}s` }}
                      >
                        <div
                          className="home-book-cover"
                          style={{ backgroundImage: `url(${book.cover_image ?? ''})` }}
                        ></div>
                      </div>
                    ))}
                    <Link to="/search" className="add-more-card">
                      <div className="add-more-content">
                        <PlusCircle size={24} />
                        <span>Find More</span>
                      </div>
                    </Link>
                  </div>
                )}
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