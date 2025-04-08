import { useState } from "react";
import { useEffect } from "react";
import { Plus } from 'lucide-react';
import '../style/style.css';
import AddPopUp from '../components/add-to-bookshelf-discussion';

export default function BookPopup({ book, onClose, userId }) {
    const [addPopupBook, setAddPopupBook] = useState(null);
    const [bookStatus, setBookStatus] = useState(null);
    const [isLoadingStatus, setIsLoadingStatus] = useState(true); 

    // const [userId, setUserId] = useState(null);
    const [isAddingPost, setIsAddingPost] = useState(false);
    const [newPostTitle, setNewPostTitle] = useState('');
    const [newPostContent, setNewPostContent] = useState('');
    const [isCommentsVisible, setIsCommentsVisible] = useState({});
    const [newComment, setNewComment] = useState('');
    // local state for testing posts
    const [posts, setPosts] = useState(book.posts || []);
    
    const fetchBookStatus = async () => {
        setIsLoadingStatus(true);
        try {
            const response = await fetch(`http://localhost:8000/shelf/api/user/${userId}/bookshelf/${book._id}/status`, {
                method: "GET",
            });

            if (!response.ok) {
                throw new Error("Failed to fetch book status");
            }

            const data = await response.json()
            if (data.status == "no-status"){
                setBookStatus("unread")
            } else if (data.status == "to-read") {
                setBookStatus("in wishlist")
            } else if (data.status == "currently-reading") {
                setBookStatus("reading")
            } else {
                setBookStatus(data.status)
            }
            
        } catch (error) {
            console.error("Error fetching book status:", error);
        } finally {
            setIsLoadingStatus(false); // Set loading state to false when done
        }
    };
    
    useEffect(() => {
        // const fetchUserProfile = async () => {
        //     const token = localStorage.getItem("access_token");
    
        //     if (!token) {
        //         console.error("No access token found.");
        //         return;
        //     }
    
        //     try {
        //         const response = await fetch("http://localhost:8000/user/profile", {
        //             method: "GET",
        //             headers: {
        //                 Authorization: `Bearer ${token}`,
        //             },
        //         });
    
        //         if (!response.ok) {
        //             throw new Error("Failed to fetch user profile");
        //         }
    
        //         const data = await response.json();
        //         setUserId(data.id);
        //         fetchBookStatus(data.id); // Ensure the user ID is set properly
        //     } catch (error) {
        //         console.error("Error fetching user profile:", error);
        //     }
        // };

        fetchBookStatus();
        
    }, []); // Run only on component mount
    
    const toggleComments = (postIndex) => {
        setIsCommentsVisible(prevState => ({
            ...prevState,
            [postIndex]: !prevState[postIndex],
        }));
    };

    const handleAddPost = () => {
        setIsAddingPost(true);
    };

    const handleCancelNewPost = () => {
        setIsAddingPost(false);
        setNewPostTitle('');
        setNewPostContent('');
    };

    const handleAddNewPost = () => {
        const newPost = {
            username: "Test User", // test data
            title: newPostTitle,
            content: newPostContent,
            comments: [],
        };
        setPosts([newPost, ...posts]); // test state
        handleCancelNewPost();
    };

    const handleAddComment = (postIndex) => {
        const updatedPosts = [...posts];
        const newCommentData = {
            content: newComment,
            username: "Test User", // test data
        };
        updatedPosts[postIndex].comments.push(newCommentData);
        setPosts(updatedPosts);
        setNewComment('');
    };

    const handleCommentChange = (e) => {
        setNewComment(e.target.value);
    };


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
                    rating: "mid",
                }),
            });
    
            if (response.ok) {
                fetchBookStatus(); // Re-fetch the book status after updating
            }

            return response;

        } catch (error) {
        console.error(`Error updating bookshelf (${status}):`, error);
        return { ok: false };
        }
    };

    return (
        <div className="popup-overlay">
            <div className="popup-container">
                <button className="popup-close" onClick={onClose}> × </button>
                <div className="popup-content">
                    <button className="add-button" onClick={(e) => openAddPopup(book, e)}>
                        Add Book to Shelf +
                    </button>
                    <div className="popup-image">
                        <img src={book.cover_image} alt={book.title} className="cover-img" />
                    </div>
                    <div className="popup-details">
                        <h2 className="popup-title">{book.title}</h2>
                        <p className="popup-author">{Array.isArray(book.author) ? book.author.join(", ") : book.author}</p>
                        {/* Display loading message while status is being fetched */}
                        {isLoadingStatus ? (
                            <p className="popup-info">Loading book status...</p>
                        ) : (
                            <p className="popup-info">Bookshelf status: {bookStatus}</p>
                        )}
                        <p className="popup-info">Page Count: {book.page_count}</p>
                        <p className="popup-info">
                            Genre: {book.genre_tags && book.genre_tags.length > 0 
                            ? book.genre_tags[0].split(" ").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ") 
                            : "Fiction"}
                        </p>
                        <p className="popup-info">Publisher: {book.publisher}</p>
                        <p className="popup-info">
                            ISBN: {Array.isArray(book.isbn) ? book.isbn[0] : book.isbn}
                        </p>
                    </div>
                </div>
                <p className="popup-description">{book.summary}</p>

                {/* Discussion Section */}
                <div className="popup-discussion">
                    <button className="add-post-btn" onClick={handleAddPost}>+</button>
                    {isAddingPost && (
                        <div className="add-post-form">
                            <input
                                type="text"
                                value={newPostTitle}
                                onChange={(e) => setNewPostTitle(e.target.value)}
                                placeholder="Post Title"
                            />
                            <textarea
                                value={newPostContent}
                                onChange={(e) => setNewPostContent(e.target.value)}
                                placeholder="Write your post..."
                            />
                            <div className="post-buttons">
                                <button onClick={handleAddNewPost}>Submit</button>
                                <button onClick={handleCancelNewPost}>Cancel</button>
                            </div>
                        </div>
                    )}

                    {/* Display Posts */}
                    {posts.length > 0 ? (
                        posts.map((post, index) => (
                            <div key={index} className="popup-post">
                                <div className="popup-post-header">
                                    <div className="popup-pfp"></div>
                                    <div className="popup-post-details">
                                        <p className="popup-username">{post.username}</p>
                                        <p className="popup-post-title">{post.title}</p>
                                        <p className="popup-post-content">{post.content}</p>
                                        <button className="comment-btn" onClick={() => toggleComments(index)}>
                                            {isCommentsVisible[index] ? "▲" : "▼"}
                                        </button>
                                        {isCommentsVisible[index] && (
                                            <div className="popup-comments">
                                                {post.comments && post.comments.length > 0 ? (
                                                    post.comments.map((comment, idx) => (
                                                        <div key={idx} className="popup-comment">
                                                            <p><strong>{comment.username}:</strong> {comment.content}</p>
                                                        </div>
                                                    ))
                                                ) : (
                                                    <p>No comments yet. Be the first to comment!</p>
                                                )}
                                                <div className="comment-form">
                                                    <textarea
                                                        value={newComment}
                                                        onChange={handleCommentChange}
                                                        placeholder="Add a comment..."
                                                    />
                                                    <div className="comment-btns">
                                                        <button onClick={() => handleAddComment(index)}>Submit</button>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="popup-no-posts">There aren't any discussion posts here yet. Start the conversation using the '+' button!</p>
                    )}
                </div>
            </div>
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
}