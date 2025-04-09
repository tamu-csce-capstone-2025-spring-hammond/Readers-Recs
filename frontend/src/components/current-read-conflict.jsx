import React from 'react';
import '../style/style.css';

const CurrentReadConflict = ({ open, currentTitle, onConfirm, onCancel }) => {
    if (!open) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-box">
                <p>You're already reading <strong>"{currentTitle}"</strong>.<br />Do you want to replace it and lose progress?</p>
                <div className="modal-actions">
                    <button className="confirm-button" onClick={onConfirm}>
                        Yes, replace
                    </button>
                    <button className="cancel-button" onClick={onCancel}>
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CurrentReadConflict;
