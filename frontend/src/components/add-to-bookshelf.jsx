import { useState } from "react";
import "../style/style.css";
import RatingPopup from "./book-rating";

export default function AddPopUp({ book, onClose, updateBookshelf, position }) {
    const handleUpdateBookshelf = async (status) => {
        const response = await updateBookshelf(book, status);
        if (response.ok) {
            alert(`Added to ${status.replace("-", " ")}!`);
        } else {
            alert(`Failed to add to ${status.replace("-", " ")}`);
        }
        onClose();
    };

    const [showRatingPopup, setShowRatingPopup] = useState(false);
    const handleFinishedClick = () => {
        setShowRatingPopup(true);
    };
    const handleRatingClick = (rating) => {
        console.log("Selected rating:", rating);
        setShowRatingPopup(false);
        onClose();
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
                        <button className="plus-button" onClick={() => updateBookshelf(book, "currently-reading")}> + </button>
                        <p>Currently Reading</p>
                    </div>
                    <div className="add-to-read">
                        <button className="plus-button" onClick={() => updateBookshelf(book, "to-read")}> + </button>
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
        </>
    );
}