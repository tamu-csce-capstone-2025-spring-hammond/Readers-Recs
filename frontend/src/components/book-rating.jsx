import React from 'react';
import { ThumbsUp, ThumbsDown, Minus, X } from 'lucide-react';
import '../style/style.css';

const RatingPopup = ({ open, currentRating, onClose, onRatingClick }) => {
    if (!open) return null;

    return (
        <div className="rating-popup-overlay">
            <div className="rating-popup-content">
                <div className="rating-thumbs">
                    <button
                        className={`thumb-btn thumbs-up ${currentRating === 'pos' ? 'selected' : ''}`}
                        onClick={() => {
                        onRatingClick('pos');
                        onClose();
                        }}
                    >
                        <ThumbsUp size={20} />
                        <span>Loved it</span>
                    </button>
                    <button
                        className={`thumb-btn thumbs-mid ${currentRating === 'mid' ? 'selected' : ''}`}
                        onClick={() => {
                        onRatingClick('mid');
                        onClose();
                        }}
                    >
                        <Minus size={20} />
                        <span>It's okay</span>
                    </button>
                    <button
                        className={`thumb-btn thumbs-down ${currentRating === 'neg' ? 'selected' : ''}`}
                        onClick={() => {
                        onRatingClick('neg');
                        onClose();
                        }}
                    >
                        <ThumbsDown size={20} />
                        <span>Not great</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RatingPopup;