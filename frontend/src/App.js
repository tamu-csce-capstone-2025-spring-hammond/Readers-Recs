import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/navbar";
import Home from "./pages/home";
import SearchBooks from "./pages/searchbooks";
import Chats from "./pages/chat";
import Profile from "./pages/profile";
import Intro from "./pages/intro";
import Login from "./pages/login";

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/intro" element={<Intro />} />
          <Route path="/login" element={<Login />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/search" element={<SearchBooks />} />
          <Route path="/chats" element={<Chats />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/nav" element={<Navbar />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
