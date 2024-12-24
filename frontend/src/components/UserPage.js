import React, { useEffect, useState } from 'react';
import PostList from './PostList';
import api from '../services/api';
import { useParams } from 'react-router-dom';
import "../styles/UserPage.css";

const UserPage = () => {
    const { username } = useParams();

    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [pagination, setPagination] = useState({ page: 1, totalPages: 1 });
    const [error, setError] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const userResponse = await api.get(`/users/${username}`);
                setUser(userResponse.data);

                setIsAuthenticated(!!localStorage.getItem('username'));
            } catch (error) {
                setError('Не вдалося отримати дані про користувача.');
                console.error('Error fetching user data:', error);
            }
        };

        const fetchUserPosts = async () => {
            try {
                const endpoint = isAuthenticated
                ? `/users/${username}/posts?page=${pagination.page}`
                    : `/users/${username}/posts`;

                const headers = isAuthenticated
                    ? {
                        'Authorization': `Basic ${btoa(
                            `${localStorage.getItem('username')}:${localStorage.getItem('password')}`
                        )}`,
                    }
                  : {
                        'Authorization': `Basic ${btoa(":")}`,
                  };       
                  const postsResponse = await api.get(endpoint, { headers });
                  if (Array.isArray(postsResponse.data)) {
                    setPosts(postsResponse.data.slice(-10));
                } else if (postsResponse.data.posts) {
                    const updatedPosts = postsResponse.data.posts.map(post => ({
                    ...post,
                    is_liked: post.is_liked, // Якщо не має is_liked, ставимо за замовчуванням false
                }));
                setPosts(updatedPosts);
                    setPagination((prev) => ({
                        ...prev,
                        totalPages: postsResponse.data.totalPages || 1,
                    }));
                } else {
                    setPosts([]);
                    console.error("Unexpected response structure:", postsResponse.data);
                }
            } catch (error) {
                console.error("Error fetching posts:", error);
                setError("An error occurred while fetching posts.");
            }
        };

        fetchUserData();
        fetchUserPosts();
    }, [username, pagination.page], isAuthenticated);

    const handlePagination = (direction) => {
        setPagination((prev) => ({
            ...prev,
            page: prev.page + direction,
        }));
    };

    const handleLike = (postId) => {
        if (posts.find(post => post.id === postId).is_liked) {
            return; // Якщо лайк вже поставлений, не відправляти запит
        }
    
        api.put(`/users/${username}/posts/${postId}/like`, {}, {
            headers: {
                'Authorization': `Basic ${btoa(
                    `${localStorage.getItem('username')}:${localStorage.getItem('password')}`
                )}`,
            },
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
        .catch((error) => {
            console.error('Error liking post:', error);
            alert("Не вдалося поставити лайк.");
        });
    };
    
    const handleUnlike = (postId) => {
        if (!posts.find(post => post.id === postId).is_liked) {
            return; // Якщо лайк не поставлений, не відправляти запит
        }
    
        api.delete(`/users/${username}/posts/${postId}/like`, {
            headers: {
                'Authorization': `Basic ${btoa(
                    `${localStorage.getItem('username')}:${localStorage.getItem('password')}`
                )}`,
            },
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
            alert("Не вдалося зняти лайк.");
        });
    };

    if (error) return <div>{error}</div>;

    if (!user) return <div>Завантаження...</div>;

    return (
        <div className='userpage-container'>
            <div className="user-info">
                <h1 className='title'>Сторінка користувача {username}</h1>
                <div className='userpage-card'>
                    <h2 className='section-title'>Інформація про користувача</h2>
                    <p><strong>Username:</strong> {user.username}</p>
                    <p><strong>Full name:</strong> {user.full_name}</p>
                </div>
            </div>

            <div className='posts-section'> 
                <h2 className='section-title'>Пости користувача</h2>
                <PostList posts={posts} onLike={handleLike} onUnlike={handleUnlike}/>
                {isAuthenticated && pagination.totalPages > 1 && (
                    <div className="pagination">
                        <button
                            onClick={() => handlePagination(-1)}
                            disabled={pagination.page === 1}
                            className="button"
                        >
                            Попередня сторінка
                        </button>
                        <button
                        onClick={() => handlePagination(1)}
                        disabled={pagination.page === pagination.totalPages}
                        className="button"
                        >
                            Наступна сторінка
                        </button>
                    </div>
                )}

                {!isAuthenticated && posts.length > 0 && posts.length <= 10 && (
                    <p className="auth-prompt">Авторизуйтесь, щоб побачити більше постів.</p>
                )}
            </div>
        </div>
    );
};

export default UserPage;
