import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";

const Login = () => {
  // Initialize useNavigate hook for navigation
  const navigate = useNavigate();

  // Success handler for Google Login
  const handleSuccess = (response) => {
    console.log("Google Login Success:", response);

    // You can store user info or token here if needed, e.g., in localStorage or context
    // localStorage.setItem("userToken", response.credential);

    // Redirect to the home page ("/")
    navigate("/");
  };

  // Failure handler for Google Login
  const handleFailure = (error) => {
    console.error("Google Login Failed:", error);
  };

  return (
    <div className="login-container">
      <h1>Login with Google</h1>
      <GoogleLogin onSuccess={handleSuccess} onError={handleFailure} />
    </div>
  );
};

export default Login;
