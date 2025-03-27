import { Link } from "react-router-dom";
import React, { useState } from "react";
import "../style/style.css";
import logo from "../assets/logo.png";
import { Search, MessageSquare, User } from "lucide-react";

const Navbar = () => {
  return (
    <nav className="navbar">
      <Link to="/home" className="logo-button">
        <img src={logo} alt="Reader's Recs Logo" />
      </Link>
      <Link to="/search" className="nav-button">
        <Search />
        <span>Search</span>
      </Link>
      <Link to="/chats" className="nav-button">
        <MessageSquare/>
        <span>Chats</span>
      </Link>
      <Link to="/profile" className="nav-button">
        <User />
        <span>Profile</span>
      </Link>
    </nav>
  );
};

export default Navbar;
