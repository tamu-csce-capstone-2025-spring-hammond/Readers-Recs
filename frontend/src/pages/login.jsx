import React, { useState } from 'react';
import { Mail, Lock, ArrowRight } from 'lucide-react';
import '../style/login.scss';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (email && password) {
      console.log('Login attempted with:', email);
      // In a real implementation, send these credentials to your server
      // loginUser(email, password);
    } else {
      alert('Please enter both email and password');
    }
  };

  const handleGoogleLogin = () => {
    // initialize the Google OAuth flow here
    console.log('Google sign-in clicked');
    // Example to do:
    // googleAuth.signIn().then(handleSignIn).catch(handleError);
  };

  return (
    <div className='login-page'>
    <div className="login-container">
      <div className="login-header">
        <h1>Welcome Back</h1>
        <p>Sign in to continue to your account</p>
      </div>
      <div className="login-form">
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <div className="input-wrapper">
              <Mail size={18} className="input-icon" />
              <input 
                type="email" 
                id="email" 
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock size={18} className="input-icon" />
              <input 
                type="password" 
                id="password" 
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <a href="#" className="forgot-password">Forgot password?</a>
          </div>
          <button type="submit" className="login-button">
            Sign In
            <ArrowRight size={18} />
          </button>
        </form>
        
        <div className="divider">
          <span>OR</span>
        </div>
        
        <div className="oauth-container">
          <button className="google-button" onClick={handleGoogleLogin}>
            <svg className="google-icon" width="18" height="18" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              <path fill="none" d="M1 1h22v22H1z" />
            </svg>
            Sign in with Google
          </button>
        </div>
        
        <div className="signup-link">
          Don't have an account? <a href="#">Sign up</a>
        </div>
      </div>
    </div>
    </div>
  );
};

export default Login;