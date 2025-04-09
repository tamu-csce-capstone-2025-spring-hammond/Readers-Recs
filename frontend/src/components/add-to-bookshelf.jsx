import { useState } from "react";
import "../style/style.css";
import RatingPopup from "./book-rating";
import CurrentReadConflict from "./current-read-conflict";


export default function AddPopUp({ book, onClose, updateBookshelf, position, currentReading, setCurrentReading }) {
    const handleUpdateBookshelf = async (book, status, rating) => {
        const response = await updateBookshelf(book, status, rating);
        if (response.ok) {
            alert(`Added to ${status.replace("-", " ")}!`);
        } else {
            alert(`Failed to add to ${status.replace("-", " ")}`);
        }
        onClose();
    };
    const [showConflict, setShowConflict] = useState(false);
    const [pendingStatus, setPendingStatus] = useState(null);
    const [showRatingPopup, setShowRatingPopup] = useState(false);
    const handleFinishedClick = () => {
        console.log("HANDLE FINSH CLICK")
        setShowRatingPopup(true);
    };
    const handleRatingClick = (rating) => {
        console.log("Selected rating:", rating);
        setShowRatingPopup(false);
        handleUpdateBookshelf(book, "read", rating)
        onClose();
    };
    const handleConfirmConflict = () => {
        setShowConflict(false);
        handleUpdateBookshelf(book, pendingStatus, "mid");
        setCurrentReading(book);
    };
    const handleCancelConflict = () => {
        setShowConflict(false);
        setPendingStatus(null);
        onClose(); // close the whole add popup
    };

    return (
        <>
            <div
                className="add-box"
                style={{
                    position: "absolute",
                    top: position?.top + "px",
                    left: position?.left + "px",
                    transform: "translate(-100%, 0)",
                    zIndex: 1000,
                }}
            >
                <button className="add-popup-close" onClick={onClose}> × </button>
                <div className="things-to-add-to">
                    <div className="add-current">
                        <button className="plus-button"
                            onClick={() => {
                                if (
                                    currentReading &&
                                    currentReading.id !== book.id &&
                                    currentReading._id !== book.id
                                ) {
                                setPendingStatus("currently-reading");
                                setShowConflict(true);
                                } else {
                                    handleUpdateBookshelf(book, "currently-reading", "mid");
                                }
                            }}
                        > + </button>
                        <p>Currently Reading</p>
                    </div>
                    <div className="add-to-read">
                        <button className="plus-button" onClick={() => handleUpdateBookshelf(book, "to-read", "mid")}> + </button>
                        <p>To-Read Shelf</p>
                    </div>
                    <div className="add-shelf">
                        <button className="plus-button" onClick={handleFinishedClick}> + </button>
                        <p>Finished Reading</p>
                    </div>
                </div>
            </div>
            <RatingPopup
                open={showRatingPopup}
                currentRating={null}
                onClose={() => setShowRatingPopup(false)}
                onRatingClick={handleRatingClick}
            />
            <CurrentReadConflict
                open={showConflict}
                currentTitle={currentReading?.title}
                onConfirm={handleConfirmConflict}
                onCancel={handleCancelConflict}
            />
        </>
    );
}