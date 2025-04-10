import { useState, useEffect, useCallback } from "react";
import '../style/style.css';

export default function BookPopup({ book, onClose }) {
    return (
        <div className="bookpopup-overlay">
            <div className="bookpopup-container">
                <button className="bookpopup-close" onClick={onClose}>×</button>
                <div className="bookpopup-content">
                    <div className="bookpopup-image">
                        <img src={book.cover_image} alt={book.title} className="bookpopup-cover-img" />
                    </div>
                    <div className="bookpopup-details">
                        <h2 className="bookpopup-title">{book.title}</h2>
                        <p className="bookpopup-author">
                            {Array.isArray(book.author) ? book.author.join(", ") : book.author}
                        </p>
                        <p className="bookpopup-info">Page Count: {book.page_count}</p>
                        <p className="bookpopup-info">
                            Genre: {book.genre_tags?.length
                                ? book.genre_tags[0].split(" ").map(word =>
                                    word.charAt(0).toUpperCase() + word.slice(1)).join(" ")
                                : "Fiction"}
                        </p>
                        <p className="bookpopup-info">Publisher: {book.publisher}</p>
                        <p className="bookpopup-info">
                            ISBN: {Array.isArray(book.isbn) ? book.isbn[0] : book.isbn}
                        </p>
                    </div>
                </div>
                <p className="bookpopup-description">{book.summary}</p>
            </div>
        </div>
    );
}
