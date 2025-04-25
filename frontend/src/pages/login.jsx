// import React from "react";
// import { GoogleLogin } from "@react-oauth/google";
// import { useNavigate } from "react-router-dom";
// import '../style/style.css';

// const Login = () => {
//   const navigate = useNavigate();

//   // Success handler for Google Login
//   const handleSuccess = (response) => {
//     console.log("Google Login Success:", response);

//     // Extract and store the access token
//     const token = response.credential;
//     if (token) {
//       localStorage.setItem("access_token", token);
//       console.log("Stored Access Token:", token);
//     } else {
//       console.error("No token received from Google.");
//     }

//     // Redirect to the profile page
//     navigate("/profile");
//     navigate("/home")
//   };

//   // Failure handler for Google Login
//   const handleFailure = (error) => {
//     console.error("Google Login Failed:", error);
//   };

//   return (
//     <div className="login-page">
//       <div className="loginpage-floating-books">
//         <div className="loginpage-book"></div>
//         <div className="loginpage-book"></div>
//         <div className="loginpage-book"></div>
//         <div className="loginpage-book"></div>
//         <div className="loginpage-book"></div>
//         <div className="loginpage-book"></div>
//         <div className="loginpage-book"></div>
//       </div>
//       <div className="login-container">
//         <div className="login-header">
//           <h1>Welcome Back</h1>
//           <p>Sign in to continue</p>
//         </div>
//         <div className="login-content">
//           <div className="google-login-wrapper">
//             <GoogleLogin 
//               onSuccess={handleSuccess} 
//               onError={handleFailure} 
//               theme="outline"
//               size="large"
//               text="signin_with"
//               width="350"
//               logo_alignment="center"
//               shape="rectangular"
//               custom_style={{
//                 background: 'white',
//                 color: '#2c5e4f',
//                 border: '2px solid #2c5e4f',
//                 borderRadius: '6px',
//                 padding: '10px 20px',
//                 width: '100%',
//                 display: 'flex',
//                 justifyContent: 'center',
//                 alignItems: 'center',
//                 fontWeight: '600'
//               }}
//             />
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Login;

// Modified Login.jsx
import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";
import '../style/style.css';
import { jwtDecode } from 'jwt-decode';
import BACKEND_URL from "../api";


const Login = ({ setShowGenreModal, setIsFirstTimeUser }) => {
  const navigate = useNavigate();

  // Success handler for Google Login
  const handleSuccess = async (response) => {
    console.log("Google Login Success:", response);

    // Extract and store the access token
    const token = response.credential;
    if (token) {
      localStorage.setItem("access_token", token);
      console.log("Stored Access Token:", token);
      
      try {
        // Decode the token to get user information
        const decoded = jwtDecode(token);
        const userEmail = decoded.email;
        
        // Check if user exists in your database
        const userExistsResponse = await fetch(`${BACKEND_URL}/user/check-email-exists?email=${encodeURIComponent(userEmail)}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (userExistsResponse.ok) {
          const { exists } = await userExistsResponse.json();
          
          if (!exists) {
            // This is a new user
            console.log("New user detected");
            setIsFirstTimeUser(true);
            setShowGenreModal(true);
            // // Create new user in database
            // await fetch('http://localhost:8000/user/create', {
            //   method: 'POST',
            //   headers: {
            //     'Content-Type': 'application/json',
            //     'Authorization': `Bearer ${token}`,
            //   },
            //   body: JSON.stringify({
            //     email: userEmail,
            //     name: decoded.name,
            //     picture: decoded.picture
            //   }),
            // });
          } else {
            console.log("Existing user detected");
          }
          
          // Navigate to home page
          navigate("/profile");
          navigate("/home");
        } else {
          console.error("Failed to check if user exists");
        }
      } catch (error) {
        console.error("Authentication error:", error);
        // If there's an error checking user existence, still navigate to home
        // but don't show the genre modal
        navigate("/home");
      }
    } else {
      console.error("No token received from Google.");
    }
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
