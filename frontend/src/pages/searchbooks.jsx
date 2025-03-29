import React, { useState, useEffect, useCallback } from 'react';
import { Search, Plus } from 'lucide-react';
import '../style/style.css';
import Navbar from '../components/navbar';
import BookPopUp from '../components/discussion';
import AddPopUp from '../components/add-to-bookshelf';

const SearchBooks = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('any'); // options: any, title, author, isbn
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedBook, setSelectedBook] = useState(null);
  const [addPopupBook, setAddPopupBook] = useState(null);
  const [userId, setUserId] = useState(null);

  const handleSearchChange = (e) => setSearchQuery(e.target.value);
  const handleFilterChange = (e) => setFilterType(e.target.value);

  const fetchUserProfile = async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      console.error("No access token found.");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/user/profile", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch user profile");
      }

      const data = await response.json();

      setUserId(data.id); // Extract and set the user ID
    } catch (error) {
      console.error("Error fetching user profile:", error);
    }
  };

  fetchUserProfile();

  const fetchBooks = useCallback(async () => {
    if (!searchQuery) {
      setBooks([]);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `http://localhost:8000/api/books?query=${encodeURIComponent(searchQuery)}&type=${filterType}`
      );

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch books');
      }

      setBooks(data);
    } catch (err) {
      setError(err.message);
      setBooks([]);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filterType]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setBooks([]);
      return;
    }

    const timerId = setTimeout(() => {
      fetchBooks();
    }, 500);

    return () => clearTimeout(timerId);
  }, [fetchBooks]);

  const openPopup = (book) => setSelectedBook(book);
  const closePopup = () => setSelectedBook(null);

  const openAddPopup = (book, event) => {
    event.stopPropagation();
    const rect = event.currentTarget.getBoundingClientRect();
    setAddPopupBook({ book, position: { top: rect.top, left: rect.right } });
  };

  const closeAddPopup = () => setAddPopupBook(null);

  const updateBookshelf = async (book, status) => {
    try {
      const response = await fetch(`http://localhost:8000/shelf/api/user/${userId}/bookshelf`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          book_id: book.id || book._id,
          status: status,
        }),
      });

      return response;
    } catch (error) {
      console.error(`Error updating bookshelf (${status}):`, error);
      return { ok: false };
    }
  };

  return (
    <div className="search-container">
      <div className="search-bar">
        <Search className="search-icon" size={20} />
        <input
          type="text"
          placeholder="Search books..."
          value={searchQuery}
          onChange={handleSearchChange}
        />
        <select className="filter-dropdown" value={filterType} onChange={handleFilterChange}>
          <option value="any">Any Keyword</option>
          <option value="title">Title</option>
          <option value="author">Author</option>
          <option value="isbn">ISBN</option>
        </select>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'black' }}>{error}</p>}

      <div className="search-results">
        {books.length > 0 ? (
          books.map((book) => (
            <div key={book.id || book._id} className="book-card" onClick={() => openPopup(book)}>
              <div className="book-cover">
                <img src={book.cover_image} alt={book.title} className="cover-img" />
              </div>
              <div className="book-info">
                <h2 className="book-title">{book.title}</h2>
                <p className="book-author">
                  {Array.isArray(book.author) ? book.author.join(', ') : book.author}
                  {', '}
                  {book.publication_date ? new Date(book.publication_date).getFullYear() : book.year}
                </p>
                <p className="book-description">{book.summary}</p>
              </div>
              <button className="add-button" onClick={(e) => openAddPopup(book, e)}>
                <Plus size={20} />
              </button>
            </div>
          ))
        ) : (
          !loading && <p className="no-results"></p>
        )}
      </div>

      <Navbar />

      {selectedBook && <BookPopUp book={selectedBook} onClose={closePopup} />}
      {addPopupBook && (
        <AddPopUp
          book={addPopupBook.book}
          onClose={closeAddPopup}
          updateBookshelf={updateBookshelf}
          position={addPopupBook.position}
        />
      )}
    </div>
  );
};

export default SearchBooks;
