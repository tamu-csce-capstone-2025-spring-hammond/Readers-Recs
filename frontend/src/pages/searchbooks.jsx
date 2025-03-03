import React from 'react';
import Navbar from '../components/navbar';
import SearchedBook from '../components/searched-book';
import "../style/style.css";

const SearchBooks = () => {
    return (
    <div>
        <div className='search-bar'>
            <h2><input type='text' placeholder='Search for a book'/></h2>
        </div>
        <div className='searched-books-list'>
            <SearchedBook />
            <SearchedBook />
            <SearchedBook />
        </div>
        <Navbar />
    </div>
    );
};

export default SearchBooks;