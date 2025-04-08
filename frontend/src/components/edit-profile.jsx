import { useState } from "react";
import BACKEND_URL from "../api";

const EditProfile = ({ user, onClose, refreshUser }) => {
  const [screenName, setScreenName] = useState(user.name || "");
  const [username, setUsername] = useState(user.username || "");
  const [profilePicture, setProfilePicture] = useState(user.profile_image || "");
  const [saving, setSaving] = useState(false);

  // Loading check if user data is still loading
  if (!user || (!user.id && !user._id)) {
    return <div>Loading user info...</div>;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const payload = {};

      // Handle splitting the screen name into first and last name
      if (screenName.trim()) {
        const nameParts = screenName.trim().split(' ');
        payload.first_name = nameParts[0];
        payload.last_name = nameParts.slice(1).join(' ') || "";
      }

      if (username.trim()) {
        payload.username = username.trim();
      }

      if (profilePicture.trim()) {
        payload.profile_image = profilePicture.trim();
      }

      if (Object.keys(payload).length === 0) {
        alert("No changes to save.");
        setSaving(false);
        return;
      }

      const userId = user.id || user._id;
      if (!userId) {
        alert("User ID not available.");
        setSaving(false);
        return;
      }

      const response = await fetch(`${BACKEND_URL}/user/profile/${userId}/edit-profile`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json();
        alert(data.error || "Failed to update profile.");
        setSaving(false);
        return;
      }

      alert("Profile updated successfully!");
      await refreshUser();  // 🆕 Refresh user info from backend
      onClose();            // Close popup
    } catch (err) {
      console.error("Error updating profile:", err);
      alert("Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="edit-profile-popup">
      <div className="profile-popup-content">
        <button className="close-btn" onClick={onClose}>x</button>
        <h2>Edit Profile</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Screen Name:
            <input
              type="text"
              value={screenName}
              onChange={(e) => setScreenName(e.target.value)}
            />
          </label>

          <label>
            Username:
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </label>

          <label>
            Profile Picture (URL):
            <input
              type="text"
              value={profilePicture}
              onChange={(e) => setProfilePicture(e.target.value)}
              placeholder="Paste image URL here"
            />
          </label>

          {/* Preview the profile image if available */}
          {profilePicture && (
            <img
              src={profilePicture}
              alt="Profile Preview"
              className="profile-preview"
            />
          )}

          <button
            className="submit-btn"
            type="submit"
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default EditProfile;
