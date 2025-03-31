import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import '../style/style.css';

const Login = () => {
  const navigate = useNavigate();

  // Success handler for Google Login
  const handleSuccess = (response) => {
    console.log("Google Login Success:", response);

    // Extract and store the access token
    const token = response.credential;
    if (token) {
      localStorage.setItem("access_token", token);
      // console.log("Stored Access Token:", token);
    } else {
      console.error("No token received from Google.");
    }

    // Redirect to the profile page
    navigate("/profile");
    navigate("/home")
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
