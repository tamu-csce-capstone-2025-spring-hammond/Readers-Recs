import { useState, useEffect, useCallback } from "react";
import { Plus } from 'lucide-react';
import '../style/style.css';
import AddPopUp from '../components/add-to-bookshelf-discussion';
import BACKEND_URL from "../api";

export default function BookPopup({ book, onClose, userId }) {
    const [addPopupBook, setAddPopupBook] = useState(null);
    const [bookStatus, setBookStatus] = useState(null);
    const [isLoadingStatus, setIsLoadingStatus] = useState(true); 
    const [isAddingPost, setIsAddingPost] = useState(false);
    const [newPostTitle, setNewPostTitle] = useState('');
    const [newPostContent, setNewPostContent] = useState('');
    const [isCommentsVisible, setIsCommentsVisible] = useState({});
    const [newComment, setNewComment] = useState('');
    // local state for testing posts
    const [posts, setPosts] = useState(book.posts || []);
    
    const [currentReading, setCurrentReading] = useState(null);
    const fetchCurrentReading = async (userId, token) => {
        try {
          const res = await fetch(`${BACKEND_URL}/shelf/api/user/${userId}/books/currently-reading`, {
            headers: { Authorization: `Bearer ${token}` },
          });
      
          if (res.ok) {
            const data = await res.json();
            setCurrentReading(data);
            console.log("Current Reading:", data);
          } else {
            setCurrentReading(null);
          }
        } catch (err) {
          console.error("Error fetching currently reading book:", err);
        }
      };

    const fetchBookStatus = async () => {
        setIsLoadingStatus(true);
        try {
            const response = await fetch(`${BACKEND_URL}/shelf/api/user/${userId}/bookshelf/${book._id}/status`, {
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
        const fetchUserProfile = async () => {
            const token = localStorage.getItem("access_token");
    
            if (!token) {
                console.error("No access token found.");
                return;
            }
    
            try {
                const response = await fetch(`${BACKEND_URL}/user/profile`, {
                    method: "GET",
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
    
                if (!response.ok) {
                    throw new Error("Failed to fetch user profile");
                }
    
                const data = await response.json();
                await fetchCurrentReading(data.id, token);
            } catch (error) {
                console.error("Error fetching user profile:", error);
            }
        };
    
        fetchUserProfile();
    }, []); // Run only on component mount

    // Fetch posts
    const fetchPosts = useCallback(async () => {
        try {
            const response = await fetch(`${BACKEND_URL}/api/books/${book._id}/posts`);
            const data = await response.json();
            if (response.ok) {
              setPosts(data);
            } else {
              console.error('Error fetching posts:', data.error);
            }
        } catch (error) {
            console.error('Error fetching posts:', error);
        }
      }, [book._id]);
  
      useEffect(() => {
          fetchPosts();
      }, [fetchPosts]);
  
      // Fetch comments
      const fetchComments = async (postId, postIndex) => {
          try {
              const response = await fetch(`${BACKEND_URL}/api/posts/${postId}/comments`);
              const data = await response.json();
              if (response.ok) {
                  const fixedComments = data.map(comment => ({
                      ...comment,
                      content: comment.comment_text
                  }));
                  const updatedPosts = [...posts];
                  updatedPosts[postIndex].comments = fixedComments;
                  setPosts(updatedPosts);
              } else {
                  console.error('Error fetching comments:', data.error);
              }
          } catch (error) {
              console.error('Error fetching comments:', error);
          }
      };
    
    const toggleComments = (postIndex) => {
        const post = posts[postIndex];
        if (!isCommentsVisible[postIndex]) {
            fetchComments(post._id, postIndex);
        }
        setIsCommentsVisible(prev => ({
            ...prev,
            [postIndex]: !prev[postIndex],
        }));
    };

    const handleAddNewPost = async () => {
      if (!newPostTitle || !newPostContent) return;
  
      try {
          const response = await fetch(`${BACKEND_URL}/api/books/${book._id}/posts`, {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({
                  user_id: userId,
                  title: newPostTitle,
                  post_text: newPostContent,
              }),
          });
  
          if (!response.ok) {
              const text = await response.text();
              console.error("Error creating post:", text);
              return;
          }

          setNewPostTitle('');
          setNewPostContent('');

          const data = await response.json();
          console.log("Post created:", data);

          setIsAddingPost(false);
          await fetchPosts();
          
      } catch (error) {
          console.error('Error creating post:', error);
      }
    };
     
    const handleAddComment = async (postIndex) => {
        const post = posts[postIndex];
        const commentText = newComment[postIndex];
  
        if (!commentText || !commentText.trim()) return;
  
        try {
            const response = await fetch(`${BACKEND_URL}/api/posts/${post._id}/comments`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: userId,
                    comment_text: commentText,
                    post_id: post._id,
                }),
            });
  
            if (response.ok) {
                console.log('Comment created');
                
                await fetchComments(post._id, postIndex);
                setNewComment(prev => ({
                    ...prev,
                    [postIndex]: ''
                }));
            } else {
                const text = await response.text();
                console.error('Error creating comment:', text);
            }
        } catch (error) {
            console.error('Error creating comment:', error);
        }
    };

    const handleCancelNewPost = () => {
        setIsAddingPost(false);
        setNewPostTitle('');
        setNewPostContent('');
    };

    const openAddPopup = (book, event) => {
        event.stopPropagation();
        const rect = event.currentTarget.getBoundingClientRect();
        setAddPopupBook({ book, position: { top: rect.top, left: rect.right } });
    };

    const closeAddPopup = () => setAddPopupBook(null);

    const updateBookshelf = async (book, status) => {
        try {
            const response = await fetch(`${BACKEND_URL}/shelf/api/user/${userId}/bookshelf`, {
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
                fetchBookStatus();
            }
            return response;

        } catch (error) {
            console.error(`Error updating bookshelf (${status}):`, error);
            return { ok: false };
        }
    };

    const handleCommentChange = (postIndex, value) => {
      setNewComment(prev => ({
          ...prev,
          [postIndex]: value
      }));
    };

    const renderComments = (comments, postId) => {
        return comments.map((comment, idx) => (
          <div key={idx} className="popup-comment">
            <p><strong>{comment.username || "Anonymous"}:</strong> {comment.content || comment.comment_text}</p>
      
            {/* Recursive render of replies */}
            {comment.replies && comment.replies.length > 0 && (
              <div className="popup-replies">
                {renderComments(comment.replies, postId)}
              </div>
            )}
          </div>
        ));
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
                            <p className="popup-info">Bookshelf status: {bookStatus?.split(" ").map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(" ")}</p>
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
                <p className="popup-description">
                    {book.summary?.split(" ").length > 250
                    ? book.summary.split(" ").slice(0, 250).join(" ") + "..."
                    : book.summary}
                </p>

                {/* Discussion Section */}
                <div className="popup-discussion">
                <button className="add-post-btn" onClick={() => setIsAddingPost(true)}>+</button>
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
                                <div className="profile-picture">
                                    {post.profile_picture ? (
                                        <img src={post.profile_picture} alt="Profile" className="profile-picture-img" />
                                    ) : (
                                        <div className="default-pfp" />
                                    )}
                                </div>
                                    <div className="popup-post-details">
                                        <p className="popup-username">{post.username}</p>
                                        <p className="popup-post-title">{post.title}</p>
                                        <p className="popup-post-content">{post.post_text}</p>
                                        <button className="comment-btn" onClick={() => toggleComments(index)}>
                                            {isCommentsVisible[index] ? "▲" : "▼"}
                                        </button>
                                        {isCommentsVisible[index] && (
                                            <div className="popup-comments">
                                                {post.comments && post.comments.length > 0 ? (
                                                    renderComments(post.comments, post._id)
                                                ) : (
                                                    <p>No comments yet. Be the first to comment!</p>
                                                )}
                                                <div className="comment-form">
                                                  <textarea
                                                      value={newComment[index] || ''}
                                                      onChange={(e) => handleCommentChange(index, e.target.value)}
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
                    currentReading={currentReading}
                    setCurrentReading={setCurrentReading}
                />
            )}
        </div>
    );
}
