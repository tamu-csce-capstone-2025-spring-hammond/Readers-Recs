import React from 'react';
import "../style/style.css";

const SearchedBook = () => {
    return (
        <div className='searched-book-view'>
            <div className='searched-book-left'>
                <div className='searched-book-cover'></div>
            </div>
            <div className='searched-book-right'>
                <div className='searched-book-text'>
                    <h2 id='searched-book-title'>Book Title</h2>
                    <h3 id='searched-book-author-year'>Author, Year</h3>
                    <p id='searched-book-description'>Lorem ipsum.</p>
                </div>
                <button className='round-button' id='add-book-popup'>+</button>
            </div>
        </div>
    );
};

export default SearchedBook;