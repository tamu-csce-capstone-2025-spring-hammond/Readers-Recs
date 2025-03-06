import React, { useState, useEffect } from 'react';
import { Search, Plus, BookOpen, X, Loader } from 'lucide-react';
import '../style/searchBooks.scss';
import Navbar from '../components/navbar';

const SearchBooks = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [selectedBookId, setSelectedBookId] = useState(null);
  
  // Placeholder book data
  const books = [
    {
      id: 1,
      title: "The Great Gatsby",
      author: "F. Scott Fitzgerald",
      year: "1925",
      description: "A novel set in the Roaring Twenties that explores themes of wealth, excess, and the American Dream."
    },
    {
      id: 2,
      title: "To Kill a Mockingbird",
      author: "Harper Lee",
      year: "1960",
      description: "A story of racial injustice and childhood innocence in the Deep South, seen through the eyes of Scout Finch."
    },
    {
      id: 3,
      title: "1984",
      author: "George Orwell",
      year: "1949",
      description: "A dystopian novel about a totalitarian regime that uses surveillance and mind control to oppress its citizens."
    },
    {
      id: 4,
      title: "Pride and Prejudice",
      author: "Jane Austen",
      year: "1813",
      description: "A romantic novel that critiques the British class system and explores themes of love and social expectations."
    },
    {
      id: 5,
      title: "Moby-Dick",
      author: "Herman Melville",
      year: "1851",
      description: "A whaling voyage turns into an obsession as Captain Ahab hunts the elusive white whale, Moby-Dick."
    },
    {
      id: 6,
      title: "The Catcher in the Rye",
      author: "J.D. Salinger",
      year: "1951",
      description: "A rebellious teenager, Holden Caulfield, navigates the challenges of growing up and finding meaning in life."
    },
    {
      id: 7,
      title: "Brave New World",
      author: "Aldous Huxley",
      year: "1932",
      description: "A dystopian vision of a future society controlled by technology, pleasure, and social conditioning."
    },
    {
      id: 8,
      title: "Frankenstein",
      author: "Mary Shelley",
      year: "1818",
      description: "A scientist's ambition leads to the creation of a monstrous being, raising ethical questions about science and humanity."
    }
  ];
  
  // Filter books based on search query
  const filteredBooks = searchQuery.trim() === '' 
    ? books 
    : books.filter(book => 
        book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        book.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
        book.year.includes(searchQuery)
      );
  
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setIsSearching(true);
  };
  
  // Simulate search delay
  useEffect(() => {
    if (isSearching) {
      const timer = setTimeout(() => {
        setIsSearching(false);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [searchQuery, isSearching]);
  
  // Toggle book selection for expanded view
  const toggleBookSelection = (id) => {
    setSelectedBookId(selectedBookId === id ? null : id);
  };
  
  // Handle add book button
  const handleAddBook = (e, bookId) => {
    e.stopPropagation();
    // Add to "To Read" shelf functionality would go here
    alert(`Book ID ${bookId} added to your shelf!`);
  };

  return (
    <div className="search-container">
      <div className="search-bar">
        <Search className="search-icon" size={20} />
        <input
          type="text"
          placeholder="Search by title, author, or year..."
          value={searchQuery}
          onChange={handleSearchChange}
        />
        {searchQuery && (
          <X 
            size={18} 
            className="search-clear" 
            onClick={() => setSearchQuery('')}
            style={{ cursor: 'pointer', color: 'rgba(235, 232, 225, 0.7)' }}
          />
        )}
      </div>
      
      <div className="search-results">
        {isSearching ? (
          <div className="search-loading">
            <Loader size={30} className="loading-icon" />
          </div>
        ) : filteredBooks.length > 0 ? (
          filteredBooks.map(book => (
            <div 
              key={book.id} 
              className={`book-card ${selectedBookId === book.id ? 'expanded' : ''}`}
              onClick={() => toggleBookSelection(book.id)}
            >
              <div className="book-cover">
                {/* Book cover design - would be an image in production */}
              </div>
              <div className="book-info">
                <h2 className="book-title">{book.title}</h2>
                <p className="book-author">{book.author}, {book.year}</p>
                <p className="book-description">{book.description}</p>
                
                {selectedBookId === book.id && (
                  <button className="view-details-button">
                    <BookOpen size={16} />
                    <span>View Details</span>
                  </button>
                )}
              </div>
              <button 
                className="add-button"
                onClick={(e) => handleAddBook(e, book.id)}
                aria-label="Add to shelf"
              >
                <Plus size={20} />
              </button>
            </div>
          ))
        ) : (
          <div className="no-results">
            <h3>No books found</h3>
            <p>Try adjusting your search terms or browse our recommendations</p>
          </div>
        )}
      </div>
      <Navbar/>
    </div>
  );
};

export default SearchBooks;