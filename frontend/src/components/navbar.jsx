// import { Link } from "react-router-dom";
// import "../style/navbar.scss";
// import logo from "../assets/logo.png";
// import { Search, MessageSquare, User } from "lucide-react";

// const Navbar = () => {
//   return (
//     <nav className="navbar">
//       <Link to="/" className="logo-button">
//         <img src={logo} alt="Reader's Recs Logo" />
//       </Link>
//       <Link to="/search" className="nav-button">
//         <Search />
//         <span>Search</span>
//       </Link>
//       <Link to="/chats" className="nav-button">
//         <MessageSquare/>
//         <span>Chats</span>
//       </Link>
//       <Link to="/profile" className="nav-button">
//         <User />
//         <span>Profile</span>
//       </Link>
//     </nav>
//   );
// };

// export default Navbar;

import { Link, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { Search, MessageSquare, User, Home } from "lucide-react";
import "../style/navbar.scss";
import logo from '../assets/logo.png'
const Navbar = () => {
  const location = useLocation();
  const [scrolled, setScrolled] = useState(false);
  
  // Add scroll effect
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 20;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [scrolled]);

  // Check if current route matches the link
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  return (
    <nav className={`navbar ${scrolled ? "navbar-scrolled" : ""}`}>
      <div className="navbar-container">
        <Link to="/intro" className="logo-container">
          <img src={logo} alt="Reader's Recs Logo" className="logo" />
        </Link>
        
        <div className="nav-links">
          <Link to="/" className={`nav-item ${isActive("/") ? "active" : ""}`}>
            <div className="icon-container">
              <Home />
            </div>
            <span className="link-text">Home</span>
          </Link>
          
          <Link to="/search" className={`nav-item ${isActive("/search") ? "active" : ""}`}>
            <div className="icon-container">
              <Search />
            </div>
            <span className="link-text">Search</span>
          </Link>
          
          <Link to="/chats" className={`nav-item ${isActive("/chats") ? "active" : ""}`}>
            <div className="icon-container">
              <MessageSquare />
            </div>
            <span className="link-text">Chats</span>
          </Link>
          
          <Link to="/profile" className={`nav-item ${isActive("/profile") ? "active" : ""}`}>
            <div className="icon-container">
              <User />
            </div>
            <span className="link-text">Profile</span>
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;