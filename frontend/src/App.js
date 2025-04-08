// import React from "react";
// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import { GoogleOAuthProvider } from '@react-oauth/google';
// import Navbar from "./components/navbar";
// import Home from "./pages/home";
// import SearchBooks from "./pages/searchbooks";
// import Chats from "./pages/chat";
// import Profile from "./pages/profile";
// import Intro from "./pages/intro";
// import Login from "./pages/login";
// import GenreSelectionModal from "./components/onboard";


// const GOOGLE_CLIENT_ID = "833812268493-2arm59qbfe20qlilprarcvc8coe2c5l9.apps.googleusercontent.com";

// function App() {
//   return (
//     <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
//       <Router>
//         <div className="app">
//         <GenreSelectionModal />
//           <Routes>
//             <Route path="/home" element={<Home />} />
//             <Route path="/" element={<Intro />} />
//             <Route path="/login" element={<Login />} />
//             <Route path="/profile" element={<Profile />} />
//             <Route path="/search" element={<SearchBooks />} />
//             <Route path="/chats" element={<Chats />} />
//             <Route path="/nav" element={<Navbar />} />
//             <Route path="/uo" element={<GenreSelectionModal />} />
//           </Routes>
//         </div>
//       </Router>
//     </GoogleOAuthProvider>
//   );
// }

// export default App;

import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { GoogleOAuthProvider } from '@react-oauth/google';
import Navbar from "./components/navbar";
import Home from "./pages/home";
import SearchBooks from "./pages/searchbooks";
import Chats from "./pages/chat";
import Profile from "./pages/profile";
import Intro from "./pages/intro";
import Login from "./pages/login";
import GenreSelectionModal from "./components/onboard";

const GOOGLE_CLIENT_ID = "833812268493-2arm59qbfe20qlilprarcvc8coe2c5l9.apps.googleusercontent.com";

function App() {
  const [isFirstTimeUser, setIsFirstTimeUser] = useState(false);
  const [showGenreModal, setShowGenreModal] = useState(false);

  const handleGenreSelection = () => {
    setShowGenreModal(false);
    setIsFirstTimeUser(false);
  };

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <Router>
        <div className="app">
          {showGenreModal && <GenreSelectionModal onComplete={handleGenreSelection} />}
          <Routes>
            <Route path="/home" element={<Home />} />
            <Route path="/" element={<Intro />} />
            <Route path="/login" element={<Login setShowGenreModal={setShowGenreModal} setIsFirstTimeUser={setIsFirstTimeUser} />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/search" element={<SearchBooks />} />
            <Route path="/chats" element={<Chats />} />
            <Route path="/nav" element={<Navbar />} />
          </Routes>
        </div>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
