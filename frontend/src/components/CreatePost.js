import React, { useState } from 'react';
import api from '../services/api';

const CreatePost = ({ onPostCreated }) => {
    const [content, setContent] = useState('');
    const [error, setError] = useState(null);
    const username = localStorage.getItem('username');
    const password = localStorage.getItem('password');

    const handleContentChange = (event) => {
        setContent(event.target.value);
    };

    const handleSubmit = (event) => {
        event.preventDefault();
        
        if (!username || !password) {
            setError('Будь ласка, увійдіть, щоб створити пост.');
            return;
        }

        // Запит на створення нового посту
        api.post(`/users/${username}/posts`, {
            content: content,
        }, {
            headers: {
                'Authorization': `Basic ${btoa(`${username}:${password}`)}`
            }
        })
        .then(response => {
            onPostCreated(response.data); 
            setContent('');
        })
        .catch(error => {
            setError('Помилка при створенні посту. Спробуйте знову.');
            console.error('Error creating post:', error);
        });
    };

    return (
        <div>
            <h2>Створити новий пост</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <textarea
                    value={content}
                    onChange={handleContentChange}
                    placeholder="Введіть ваш пост..."
                    rows="4"
                    cols="50"
                />
                <div>
                    <button type="submit" disabled={!content}>Опублікувати</button>
                </div>
            </form>
        </div>
    );
};

export default CreatePost;
