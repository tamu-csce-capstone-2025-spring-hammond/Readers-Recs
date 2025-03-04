import React, { useState } from 'react';
import { Search, Plus } from 'lucide-react';
import '../style/searchBooks.scss';
import Navbar from '../components/navbar';

const SearchBooks = () => {
  const [searchQuery, setSearchQuery] = useState('');
  
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

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div className="search-container">
      <div className="search-bar">
        <Search className="search-icon" size={20} />
        <input
          type="text"
          placeholder="Search"
          value={searchQuery}
          onChange={handleSearchChange}
        />
      </div>

      <div className="search-results">
        {books.map(book => (
          <div key={book.id} className="book-card">
            <div className="book-cover"></div>
            <div className="book-info">
              <h2 className="book-title">{book.title}</h2>
              <p className="book-author">{book.author}, {book.year}</p>
              <p className="book-description">{book.description}</p>
            </div>
            <button className="add-button">
              <Plus size={20} />
            </button>
          </div>
        ))}
      </div>
      <Navbar/>
    </div>
  );
};

export default SearchBooks;
