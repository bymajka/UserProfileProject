import React, { useEffect, useState } from 'react';
import api from '../services/api';
import PostList from './PostList';
import CreatePost from './CreatePost';
import { Navigate } from 'react-router-dom'; 
import "../styles/UserProfile.css";

const UserProfile = () => {
    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [pagination, setPagination] = useState({ page: 1, totalPages: 1 });
    const [error, setError] = useState(null);
    const username = localStorage.getItem('username');
    const password = localStorage.getItem('password');

    useEffect(() => {
        if (username && password) {
            // Запит для отримання даних користувача
            api.get('/me', {
                headers: {
                    'Authorization': `Basic ${btoa(`${username}:${password}`)}`
                }
            })
            .then(response => {
                setUser(response.data);
            })
            .catch(error => {
                setError('Невдала авторизація. Будь ласка, увійдіть.');
                console.error('Error fetching user data:', error);
            });
    
            // Запит для отримання публікацій користувача
            api.get(`/users/${username}/posts?page=${pagination.page}`, {
                headers: {
                    'Authorization': `Basic ${btoa(`${username}:${password}`)}`
                }
            })
            .then(response => {
                console.log(response.data);
                setPosts(response.data);
                setPagination(prev => ({
                    ...prev,
                    totalPages: response.data.totalPages,
                }));
            })
            .catch(error => {
                console.error('Error fetching posts:', error);
            });
        } else {
            setError('Користувач не авторизований.');
        }
    }, [pagination.page]);

    const handlePagination = (direction) => {
        setPagination((prev) => ({
            ...prev,
            page: prev.page + direction,
        }));
    };

    const handleLike = (postId) => {

        api.put(`/users/${username}/posts/${postId}/like`, {}, {
            headers: {
                'Authorization': `Basic ${btoa(`${username}:${password}`)}`
            }
        })
        .then(() => {
            setPosts((prevPosts) => 
                prevPosts.map((post) => 
                    post.id === postId 
                        ? { ...post, is_liked: true, likes: post.likes + 1 } 
                        : post
                )
            );
        })
        .catch(error => console.error('Error liking post:', error));
    };

    const handleUnlike = (postId) => {

        api.delete(`/users/${username}/posts/${postId}/like`, {
            headers: {
                'Authorization': `Basic ${btoa(`${username}:${password}`)}`
            }
        })
        .then(() => {
            setPosts((prevPosts) => 
                prevPosts.map((post) => 
                    post.id === postId 
                        ? { ...post, is_liked: false, likes: post.likes - 1 } 
                        : post
                )
            );
        })
        .catch((error) => {
            console.error('Error unliking post:', error);
        });
    };

    const handlePostCreated = (newPost) => {
        setPosts((prevPosts) => [newPost, ...prevPosts]);
    }

    if (error) return <Navigate to="/login" />;

    if (!user) return <div className="user-profile__loading">Loading...</div>;

    return (
        <div className="user-profile">
            <h1 className="user-profile__title">Моя сторінка</h1>
            <div className="user-profile__info">
                <h2 className="user-profile__subtitle">Інформація про користувача</h2>
                <p><strong>Username:</strong> {user.username}</p>
                <p><strong>Full name:</strong> {user.full_name}</p>
            </div>

            <div className="user-profile__posts">
                <h2 className="user-profile__subtitle">Мої пости</h2>
                <PostList posts={posts} onLike={handleLike} onUnlike={handleUnlike}/>
                <CreatePost onPostCreated={handlePostCreated} />
                <div className="user-profile__pagination">
                    <button 
                        className="user-profile__button"
                        onClick={() => handlePagination(-1)} 
                        disabled={pagination.page === 1}>
                        Попередня сторінка
                    </button>
                    <button 
                        className="user-profile__button"
                        onClick={() => handlePagination(1)} 
                        disabled={pagination.page === pagination.totalPages}>
                        Наступна сторінка
                    </button>
                </div>
            </div>
        </div>
    );
};

export default UserProfile;
