import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const GenreSelectionModal = ({ onComplete }) => {
  const navigate = useNavigate();
  const [selectedGenres, setSelectedGenres] = useState([]);

  const genres = [
    "Romance",
    "Thriller/Horror",
    "Fantasy",
    "Historical/Western",
    "Realistic",
    "Children's",
    "Crime/Mystery", 
    "Classics",
    "Self-Help",
    "Religion",
    "Nonfiction",
    "Science Fiction",
  ];

  const handleGenreSelect = (genre) => {
    if (selectedGenres.includes(genre)) {
      setSelectedGenres(selectedGenres.filter(g => g !== genre));
    } else {
      setSelectedGenres([...selectedGenres, genre]);
    }
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        console.error("No access token found");
        return;
      }

      // API Call for Recommendations
      const rec_response = await fetch(`http://localhost:8000/recs/api/user/onboarding/recommendations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({genres: selectedGenres})
      });
      if (rec_response.ok) {
        console.log("Genres added to rec model successfully");
      } else {
        console.log(rec_response);
        console.error("Failed to add :(");
      }

      // to be implemented
      // Make API call to save the genres
      const response = await fetch('http://localhost:8000/user/save-genres', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ genres: selectedGenres }),
      });

      if (response.ok) {
        console.log("Genres saved successfully");
        window.location.href = "/home";

        if (onComplete) onComplete();
      } else {
        console.error("Failed to save genres");
        if (onComplete) onComplete();
      }
    } catch (error) {
      console.error("Error saving genres:", error);
      if (onComplete) onComplete();
    }
   
  };

  return (
    <div className="genre-modal-overlay">
      <div className="genre-modal">
        <h2>Welcome to Reader's Recs!</h2>
        <p>Tell us which genres you enjoy reading (select at least 3)</p>
        
        <div className="genre-grid">
          {genres.map((genre) => (
            <button
              key={genre}
              className={`genre-button ${selectedGenres.includes(genre) ? 'selected' : ''}`}
              onClick={() => handleGenreSelect(genre)}
            >
              {genre}
            </button>
          ))}
        </div>
        
        <button 
          className={`continue-button ${selectedGenres.length >= 3 ? 'active' : 'disabled'}`}
          onClick={selectedGenres.length >= 3 ? handleSubmit : undefined}
          disabled={selectedGenres.length < 3}
        >
          Continue to Home
        </button>
      </div>
    </div>
  );
};

export default GenreSelectionModal;