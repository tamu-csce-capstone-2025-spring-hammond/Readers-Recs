import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import '../style/style.css';

const Login = () => {
  // Initialize useNavigate hook for navigation
  const navigate = useNavigate();

  // Success handler for Google Login
  const handleSuccess = (response) => {
    console.log("Google Login Success:", response);

    // You can store user info or token here if needed, e.g., in localStorage or context
    // localStorage.setItem("userToken", response.credential);

    // Redirect to the home page ("/")
    navigate("/home");
  };

  // Failure handler for Google Login
  const handleFailure = (error) => {
    console.error("Google Login Failed:", error);
  };

  return (
    <div className="login-page">
      <div className="loginpage-floating-books">
      <div className="loginpage-book"></div>
      <div className="loginpage-book"></div>
      <div className="loginpage-book"></div>
      <div className="loginpage-book"></div>
      <div className="loginpage-book"></div>
      <div className="loginpage-book"></div>
      <div className="loginpage-book"></div>
    </div>
      <div className="login-container">
        <div className="login-header">
          <h1>Welcome Back</h1>
          <p>Sign in to continue</p>
        </div>
        <div className="login-content">
          <div className="google-login-wrapper">
            <GoogleLogin 
              onSuccess={handleSuccess} 
              onError={handleFailure} 
              theme="outline"
              size="large"
              text="signin_with"
              width="350"
              logo_alignment="center"
              shape="rectangular"
              custom_style={{
                background: 'white',
                color: '#2c5e4f',
                border: '2px solid #2c5e4f',
                borderRadius: '6px',
                padding: '10px 20px',
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                fontWeight: '600'
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;