import React from "react";
import api from "../services/api";

const LikeButton = ({ postId, username }) => {
  const handleLike = async () => {
    try {
      await api.put(`/users/${username}/posts/${postId}/like`);
      alert("Post liked");
    } catch (err) {
      alert("Failed to like post");
    }
  };

  return <button onClick={handleLike}>Like</button>;
};

export default LikeButton;
