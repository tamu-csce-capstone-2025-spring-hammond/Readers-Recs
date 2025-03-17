import { useState } from "react";
import '../style/style.css';

export default function BookPopup({ book, onClose }) {
    return (
    <div className="popup-overlay">
        <div className="popup-container">
            <button className="popup-close" onClick={onClose}> × </button>
            <div className="popup-content">
                <div className="popup-image"></div>
                <div className="popup-details">
                    <h2 className="popup-title">{book.title}</h2>
                    <p className="popup-author">{book.author}, {book.year}</p>
                    <p className="popup-info">Page Count: {book.pageCount}</p>
                    <p className="popup-info">Genre: {book.genre}</p>
                    <p className="popup-info">Publisher: {book.publisher}</p>
                    <p className="popup-info">Publication Date: {book.publicationDate}</p>
                    <p className="popup-info">ISBN: {book.isbn}</p>
                </div>
            </div>
            <p className="popup-description">{book.description}</p>
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
