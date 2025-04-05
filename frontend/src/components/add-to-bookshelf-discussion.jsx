import { useState } from "react";
import "../style/style.css";

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

    return (
        <div
            className="add-box-discussion"
            style={{
                position: "absolute",
                top: position?.top + "px",
                left: position?.left + "px",
                transform: "translate(-100%, 0)",
                zIndex: 1000,
            }}
        >
            <button className="add-popup-close-discussion" onClick={onClose}> × </button>
            <div className="things-to-add-to">
                <div className="add-current">
                    <button className="plus-button-discussion" onClick={() => handleUpdateBookshelf("currently-reading")}> + </button>
                    <p>Currently Reading</p>
                </div>
                <div className="add-to-read">
                    <button className="plus-button-discussion" onClick={() => handleUpdateBookshelf("to-read")}> + </button>
                    <p>To-Read Shelf</p>
                </div>
                <div className="add-shelf">
                    <button className="plus-button-discussion" onClick={() => handleUpdateBookshelf("read")}> + </button>
                    <p>Finished Reading</p>
                </div>
            </div>
        </div>
    );
}
