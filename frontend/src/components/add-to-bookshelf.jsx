import { useState } from "react";
import "../style/style.css";

export default function AddPopup({ book, onClose, addToRead, addShelf, addCurrent, position }) {
    return (
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
                    <button className="plus-button" onClick={addCurrent}> + </button>
                    <p>Currently Reading</p>
                </div>
                <div className="add-to-read">
                    <button className="plus-button" onClick={addToRead}> + </button>
                    <p>To-Read Shelf</p>
                </div>
                <div className="add-shelf">
                    <button className="plus-button" onClick={addShelf}> + </button>
                    <p>Finished Reading</p>
                </div>
            </div>
        </div>
    );
};
