import React, { useState } from "react";

const EditProfile = ({ user, onClose }) => {
    const [screenName, setScreenName] = useState(user.name || "");
    const [username, setUsername] = useState(user.email || "");
    const [profilePicture, setProfilePicture] = useState(user.profile_picture || "");

    return (
        <div className="edit-profile-popup">
            <div className="profile-popup-content">
                <button className="close-btn" onClick={onClose}>x</button>
                <h2>Edit Profile</h2>
                <form>
                    <label>
                        Screen Name: <input type="text" value={screenName} onChange={(e) => setScreenName(e.target.value)} />
                    </label>
                    <label>
                        Username: <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
                    </label>
                    <label>
                        Profile Picture:
                        <input type="file" accept="image/*" />
                    </label>
                    {profilePicture && <img src={profilePicture} alt="Profile Preview" className="profile-preview" />}
                    <button className="submit-btn" type="submit" onClick={onClose}>Save Changes</button>
                </form>
            </div>
        </div>
    );
};

export default EditProfile;
