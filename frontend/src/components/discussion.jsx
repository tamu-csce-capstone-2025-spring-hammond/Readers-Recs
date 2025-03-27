import { useState } from "react";
import '../style/style.css';

export default function BookPopup({ book, onClose }) {
    return (
    <div className="popup-overlay">
        <div className="popup-container">
            <button className="popup-close" onClick={onClose}> × </button>
            <div className="popup-content">
                <div className="popup-image">
                    <img src={book.cover_image} alt={book.title} className="cover-img" />
                </div>
                <div className="popup-details">
                    <h2 className="popup-title">{book.title}</h2>
                    <p className="popup-author">{book.author}, {book.publication_date ? new Date(book.publication_date).getFullYear() : book.year}</p>
                    <p className="popup-info">Page Count: {book.page_count}</p>
                    <p className="popup-info">
                        Genre: {book.genre_tags && book.genre_tags.length > 0
                            ? book.genre_tags[0]
                                .split(" ")
                                .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                                .join(" ")
                            : "Fiction"}
                    </p>
                    <p className="popup-info">Publisher: {book.publisher}</p>
                    <p className="popup-info">
                        Publication Date: {new Date(book.publication_date).toLocaleDateString('en-GB', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                        })}
                    </p>
                    <p className="popup-info">ISBN: {book.isbn}</p>
                </div>
            </div>
            <p className="popup-description">{book.summary}</p>
            <div className="popup-discussion">
                {book.posts && book.posts.length > 0 ? (
                    book.posts.map((post, index) => (
                    <div key={index} className="popup-post">
                        <div className="popup-post-header">
                            <div className="popup-pfp"></div>
                            <div className="popup-post-details">
                                <p className="popup-username">{post.username}</p>
                                <p className="popup-post-title">{post.title}</p>
                                <p className="popup-post-content">{post.content}</p>
                            </div>
                        </div>
                    </div>
                    ))
                ) : (
                <p className="popup-no-posts">No discussion posts available.</p>
            )}
            </div>
        </div>
    </div>
    );
}
