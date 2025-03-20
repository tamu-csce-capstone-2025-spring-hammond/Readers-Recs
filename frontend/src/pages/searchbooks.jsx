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

  // Update search query as user types
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  // Update filter type (any, title, author, isbn)
  const handleFilterChange = (e) => {
    setFilterType(e.target.value);
  };

  const fetchBooks = useCallback(async () => {
    if (!searchQuery) {
      setBooks([]);
      return;
    }
  
    setLoading(true);
    setError('');
    console.log("Fetching books from API with query:", searchQuery, "and filter:", filterType);
  
    try {
      const response = await fetch(
        `http://localhost:8000/api/books?query=${encodeURIComponent(searchQuery)}&type=${filterType}`
      );
  
      console.log("API Response Status:", response.status);
  
      const data = await response.json(); // Only parse once
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch books');
      }
  
      console.log("Books Fetched:", data);
      setBooks(data);
    } catch (err) {
      console.error("Error fetching books:", err.message);
      setError(err.message);
      setBooks([]);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, filterType]);
  

  // Call fetchBooks when searchQuery or filterType changes
  useEffect(() => {
    console.log("useEffect triggered. Search query:", searchQuery, "Filter type:", filterType);
    if (searchQuery.trim() === '') {
      setBooks([]);
      return;
    }
  
    const timerId = setTimeout(() => {
      console.log("Calling fetchBooks...");
      fetchBooks();
    }, 500);
  
    return () => clearTimeout(timerId);
  }, [fetchBooks]);
  
  const openPopup = (book) => {
    setSelectedBook(book);
  };

  const closePopup = () => {
    setSelectedBook(null);
  };

  const openAddPopup = (book, event) => {
    event.stopPropagation();
    setAddPopupBook(book);
  };

//   const closeAddPopup = () => {
//     setAddPopupBook(null);
//   };

//   const filteredBooks = books.filter((book) => {
//     const query = searchQuery.toLowerCase();

//     switch (filterType) {
//       case 'title':
//         return book.title?.toLowerCase().includes(query) || false;
//       case 'author':
//         return book.author?.toLowerCase().includes(query) || false;
//       case 'isbn':
//         return book.isbn?.includes(query) || false; // ISBN is numeric, so no `.toLowerCase()`
//       case 'any':
//       default:
//         return (
//           book.title?.toLowerCase().includes(query) ||
//           book.author?.toLowerCase().includes(query) ||
//           book.isbn?.includes(query) ||
//           book.description?.toLowerCase().includes(query) ||
//           false
//         );
//     }
//   });

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
      {error && <p style={{ color: 'red' }}>{error}</p>}

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
          !loading && <p className="no-results">No books found.</p>
        )}
      </div>

      <Navbar />
      {selectedBook && <BookPopUp book={selectedBook} onClose={closePopup} />}
      {addPopupBook && <AddPopUp book={addPopupBook} onClose={closeAddPopup} />}
    </div>
  );
};

export default SearchBooks;
