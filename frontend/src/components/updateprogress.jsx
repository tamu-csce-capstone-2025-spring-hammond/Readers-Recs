import React, { useState, useEffect } from 'react';
import "../style/style.css";

const UpdateProgress = ({ currentPage, totalPages, onUpdate }) => {
  const [pageNumber, setPageNumber] = useState(currentPage || 0);

  useEffect(() => {
    setPageNumber(currentPage || 0);
  }, [currentPage]);

  const handlePageChange = (e) => {
    const newPage = Number(e.target.value);
    if (newPage >= 0 && newPage <= totalPages) {
      setPageNumber(newPage);
    }
  };

  const handleSubmit = () => {
    const newProgress = Math.round((pageNumber / totalPages) * 100);
    onUpdate(newProgress);
  };

  return (
    <div className="update-progress-container">
      <input
        type="number"
        min="0"
        max={totalPages}
        value={pageNumber}
        onChange={handlePageChange}
        className="progress-input"
      />
      <span> / {totalPages} pages</span>
      <button onClick={handleSubmit} className="update-btn">Update</button>
    </div>
  );
};

export default UpdateProgress;