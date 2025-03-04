import React, { useEffect } from 'react';
import '../style/intro.scss';
import { useNavigate } from 'react-router-dom';
import { Home, Search, MessageCircle, User, BookOpen, UserPlus, BookMarked, ChevronDown, Target, Users, ListChecks, Scale, MessageSquare, Quote, LayoutGrid, Info, Mail, HelpCircle, Shield } from 'lucide-react';
import logo from '../assets/logo.png'; 

const Intro = () => {
  useEffect(() => {
    const fadeElements = document.querySelectorAll('.fade-in');

    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
        }
      });
    }, { threshold: 0.1 });

    fadeElements.forEach(element => {
      observer.observe(element);
    });

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();

        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);

        if (targetElement) {
          window.scrollTo({
            top: targetElement.offsetTop - 70,
            behavior: 'smooth'
          });
        }
      });
    });
  }, []);

  const navigate = useNavigate();

  return (
    <>
      {/* Header & Navigation */}
      <header>
        <div className='floating-nav'>
        <nav>
          {/* <div className="logo">
            <img src={logo} alt="Reader's Recs Logo" className="logo-image" />
          </div> */}
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#about">About</a>
            <a href="#testimonials">Testimonials</a>
          </div>
          <button className="cta-button" onClick={() => navigate('/login')}>
            <i data-lucide="user-plus" size="18"></i>
            Get Started
        </button>
        </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="floating-books">
          <div className="book"></div>
          <div className="book"></div>
          <div className="book"></div>
          <div className="book"></div>
          <div className="book"></div>
        </div>
        <div className="hero-content">
          <h1 className="hero-title fade-in">Discover Your Next Favorite Book</h1>
          <p className="hero-subtitle fade-in">Personalized recommendations based on your unique reading preferences, not corporate promotions.</p>
          <button className="cta-button fade-in">
            <i data-lucide="book-marked" size="18"></i>
            Start Your Reading Journey
          </button>
        </div>
        <div className="scroll-down">
          <i data-lucide="chevron-down" size="36"></i>
        </div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <h2 className="section-title fade-in">Why Reader's Recs?</h2>
        <div className="features-grid">
          <div className="feature-card fade-in">
            <div className="feature-icon">
              <i data-lucide="target" size="40" color="white"></i>
            </div>
            <h3 className="feature-title">Personalized Recommendations</h3>
            <p>Our advanced algorithm learns your preferences and recommends books you'll actually enjoy.</p>
          </div>
          <div className="feature-card fade-in">
            <div className="feature-icon">
              <i data-lucide="users" size="40" color="white"></i>
            </div>
            <h3 className="feature-title">Connect with Like-minded Readers</h3>
            <p>Find and chat with readers who share your unique literary tastes.</p>
          </div>
          <div className="feature-card fade-in">
            <div className="feature-icon">
              <i data-lucide="search" size="40" color="white"></i>
            </div>
            <h3 className="feature-title">Beyond Genre Matching</h3>
            <p>Discover books based on writing style, pacing, themes, and more.</p>
          </div>
          <div className="feature-card fade-in">
            <div className="feature-icon">
              <i data-lucide="message-square" size="40" color="white"></i>
            </div>
            <h3 className="feature-title">Engage in Discussions</h3>
            <p>Join lively discussions about your favorite books and genres.</p>
          </div>
          <div className="feature-card fade-in">
            <div className="feature-icon">
              <i data-lucide="list-checks" size="40" color="white"></i>
            </div>
            <h3 className="feature-title">Track Your Reading</h3>
            <p>Easily organize books as "read," "reading," or "want to read."</p>
          </div>
          <div className="feature-card fade-in">
            <div className="feature-icon">
              <i data-lucide="scale" size="40" color="white"></i>
            </div>
            <h3 className="feature-title">Unbiased Suggestions</h3>
            <p>Recommendations driven by your preferences, not corporate promotions.</p>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="about" id="about">
        <h2 className="section-title fade-in">Our Mission</h2>
        <div className="about-content">
          <div className="about-text fade-in">
            <p>At Reader's Recs, we're addressing the frustration many readers face: finding books that truly match their unique preferences.</p>
            <br />
            <p>Current recommendation systems rely heavily on popularity metrics or simple genre matching, often influenced by corporate promotions. Our solution uses advanced machine learning algorithms to provide genuinely personalized suggestions based on your reading history and preferences.</p>
            <br />
            <p>We believe reading should be accessible and enjoyable for everyone. By creating a community-driven platform free from commercial bias, we're helping readers of all types discover their next favorite book.</p>
          </div>
          <div className="about-image fade-in">
            <img src="/api/placeholder/600/400" alt="People enjoying books" />
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials" id="testimonials">
        <h2 className="section-title fade-in">Reader Stories</h2>
        <div className="testimonial-carousel">
          <div className="testimonial-slide fade-in">
            <i data-lucide="quote" size="40" color="white"></i>
            <p className="testimonial-text">"As an avid reader with specific tastes, I was tired of generic recommendations. Reader's Recs understands my preference for character-driven narratives and has introduced me to amazing books I would have never found otherwise."</p>
            <p className="testimonial-author">- Jane, Passionate Reader</p>
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="cta">
        <div className="cta-content fade-in">
          <h2 className="cta-title">Ready to Find Your Next Great Read?</h2>
          <p className="cta-text">Join Reader's Recs today and discover books tailored to your unique preferences. Connect with like-minded readers and enjoy a personalized literary journey.</p>
          <div className="cta-buttons">
            <a href="#" className="cta-primary">
              <i data-lucide="user-plus" size="18"></i>
              Sign Up Now
            </a>
            <a href="#" className="cta-secondary">
              <i data-lucide="info" size="18"></i>
              Learn More
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <div className="footer-content">
          <div className="footer-section">
            <h3 className="footer-title">Reader's Recs</h3>
            <p>Personalized book recommendations for every reader.</p>
          </div>
          <div className="footer-section">
            <h3 className="footer-title">Quick Links</h3>
            <ul className="footer-links">
              <li><a href="#features"><i data-lucide="layout-grid" size="16"></i> Features</a></li>
              <li><a href="#about"><i data-lucide="info" size="16"></i> About</a></li>
              <li><a href="#testimonials"><i data-lucide="quote" size="16"></i> Testimonials</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h3 className="footer-title">Connect</h3>
            <ul className="footer-links">
              <li><a href="#"><i data-lucide="mail" size="16"></i> Contact Us</a></li>
              <li><a href="#"><i data-lucide="help-circle" size="16"></i> Support</a></li>
              <li><a href="#"><i data-lucide="shield" size="16"></i> Privacy Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="copyright">
          <p>&copy; 2025 Reader's Recs. Texas A&M University, CSCE 482: Senior Capstone Design.</p>
        </div>
      </footer>
    </>
  );
};

export default Intro;


// import React, { useEffect } from 'react';
// import '../style/intro.scss';
// import { useNavigate } from 'react-router-dom';
// import { Home, Search, MessageCircle, User, BookOpen, UserPlus, BookMarked, ChevronDown, Target, Users, ListChecks, Scale, MessageSquare, Quote, LayoutGrid, Info, Mail, HelpCircle, Shield } from 'lucide-react';

// const Intro = () => {
//   useEffect(() => {
//     const fadeElements = document.querySelectorAll('.fade-in');

//     const observer = new IntersectionObserver(entries => {
//       entries.forEach(entry => {
//         if (entry.isIntersecting) {
//           entry.target.classList.add('active');
//         }
//       });
//     }, { threshold: 0.1 });

//     fadeElements.forEach(element => {
//       observer.observe(element);
//     });

//     document.querySelectorAll('a[href^="#"]').forEach(anchor => {
//       anchor.addEventListener('click', function (e) {
//         e.preventDefault();

//         const targetId = this.getAttribute('href');
//         const targetElement = document.querySelector(targetId);

//         if (targetElement) {
//           window.scrollTo({
//             top: targetElement.offsetTop - 70,
//             behavior: 'smooth'
//           });
//         }
//       });
//     });
//   }, []);

//   const navigate = useNavigate();

//   return (
//     <>
//       <header>
//         <nav>
//           <div className="logo">
//             <BookOpen size={24} />
//             <span>Reader's Recs</span>
//           </div>
//           <div className="nav-links">
//             <a href="#features">Features</a>
//             <a href="#about">About</a>
//             <a href="#testimonials">Testimonials</a>
//           </div>
//           <button className="cta-button" onClick={() => navigate('/login')}>
//             <UserPlus size={18} /> Get Started
//           </button>
//         </nav>
//       </header>
      
//       <section className="hero">
//         <div className="hero-content">
//           <h1 className="hero-title fade-in">Discover Your Next Favorite Book</h1>
//           <p className="hero-subtitle fade-in">Personalized recommendations based on your unique reading preferences, not corporate promotions.</p>
//           <button className="cta-button fade-in">
//             <BookMarked size={18} /> Start Your Reading Journey
//           </button>
//         </div>
//         <div className="scroll-down">
//           <ChevronDown size={36} />
//         </div>
//       </section>
      
//       <section className="features" id="features">
//         <h2 className="section-title fade-in">Why Reader's Recs?</h2>
//         <div className="features-grid">
//           <div className="feature-card fade-in">
//             <Target size={40} color="white" />
//             <h3>Personalized Recommendations</h3>
//             <p>Our advanced algorithm learns your preferences and recommends books you'll actually enjoy.</p>
//           </div>
//           <div className="feature-card fade-in">
//             <Users size={40} color="white" />
//             <h3>Connect with Like-minded Readers</h3>
//             <p>Find and chat with readers who share your unique literary tastes.</p>
//           </div>
//           <div className="feature-card fade-in">
//             <MessageSquare size={40} color="white" />
//             <h3>Engage in Discussions</h3>
//             <p>Join lively discussions about your favorite books and genres.</p>
//           </div>
//           <div className="feature-card fade-in">
//             <ListChecks size={40} color="white" />
//             <h3>Track Your Reading</h3>
//             <p>Easily organize books as "read," "reading," or "want to read."</p>
//           </div>
//           <div className="feature-card fade-in">
//             <Scale size={40} color="white" />
//             <h3>Unbiased Suggestions</h3>
//             <p>Recommendations driven by your preferences, not corporate promotions.</p>
//           </div>
//         </div>
//       </section>

//       <section className="testimonials" id="testimonials">
//         <h2 className="section-title fade-in">Reader Stories</h2>
//         <div className="testimonial-slide fade-in">
//           <Quote size={40} color="white" />
//           <p>"As an avid reader with specific tastes, I was tired of generic recommendations. Reader's Recs understands my preferences and has introduced me to amazing books I would have never found otherwise."</p>
//           <p>- Jane, Passionate Reader</p>
//         </div>
//       </section>

//       <footer>
//         <div className="footer-content">
//           <div className="footer-section">
//             <h3>Reader's Recs</h3>
//             <p>Personalized book recommendations for every reader.</p>
//           </div>
//           <div className="footer-section">
//             <h3>Quick Links</h3>
//             <ul>
//               <li><LayoutGrid size={16} /> <a href="#features">Features</a></li>
//               <li><Info size={16} /> <a href="#about">About</a></li>
//               <li><Quote size={16} /> <a href="#testimonials">Testimonials</a></li>
//             </ul>
//           </div>
//           <div className="footer-section">
//             <h3>Connect</h3>
//             <ul>
//               <li><Mail size={16} /> <a href="#">Contact Us</a></li>
//               <li><HelpCircle size={16} /> <a href="#">Support</a></li>
//               <li><Shield size={16} /> <a href="#">Privacy Policy</a></li>
//             </ul>
//           </div>
//         </div>
//         <p>&copy; 2025 Reader's Recs. Texas A&M University, CSCE 482: Senior Capstone Design.</p>
//       </footer>
//     </>
//   );
// };

// export default Intro;
