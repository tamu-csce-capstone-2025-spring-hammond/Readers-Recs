import { useState } from "react";
import '../style/style.css';

export default function BookPopup({ book, onClose }) {
    const [isAddingPost, setIsAddingPost] = useState(false);
    const [newPostTitle, setNewPostTitle] = useState('');
    const [newPostContent, setNewPostContent] = useState('');
    const [isCommentsVisible, setIsCommentsVisible] = useState({});
    const [newComment, setNewComment] = useState('');
    // local state for testing posts
    const [posts, setPosts] = useState(book.posts || []);

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
                        <p className="popup-author">{book.author}</p>
                        <p className="popup-info">Page Count: {book.page_count}</p>
                        <p className="popup-info">Genre: {book.genre_tags && book.genre_tags.length > 0 ? book.genre_tags[0] : "Fiction"}</p>
                        <p className="popup-info">Publisher: {book.publisher}</p>
                        <p className="popup-info">ISBN: {book.isbn}</p>
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
        </div>
    );
}