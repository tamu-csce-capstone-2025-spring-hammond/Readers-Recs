import React, { useState } from 'react';
import '../style/updateprogress.scss';

const UpdateProgress = ({ currentProgress, onUpdate }) => {
  const [progress, setProgress] = useState(currentProgress);

  const handleChange = (e) => {
    setProgress(e.target.value);
  };

  const handleSubmit = () => {
    onUpdate(progress);
  };

  return (
    <div className="update-progress-container">
      <input 
        type="range" 
        min="0" 
        max="100" 
        value={progress} 
        onChange={handleChange} 
        className="progress-slider"
      />
      <span>{progress}%</span>
      <button onClick={handleSubmit} className="update-btn">Update</button>
    </div>
  );
};

export default UpdateProgress;
