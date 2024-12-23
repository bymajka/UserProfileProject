import React, { useState } from "react";
import api from "../services/api";

const NewPost = () => {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title || !content) {
      setError("Both fields are required.");
      return;
    }

    try {
      const response = await api.post("/users/me/posts", {
        title,
        content,
      });
      alert("Post created successfully");
    } catch (err) {
      setError("Failed to create post.");
    }
  };

  return (
    <div>
      <h2>Create a New Post</h2>
      {error && <p>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          ></textarea>
        </div>
        <button type="submit">Post</button>
      </form>
    </div>
  );
};

export default NewPost;
