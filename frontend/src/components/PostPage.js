import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';

const PostPage = () => {
    const { username, post_id } = useParams();
    const [post, setPost] = useState(null);
    const [error, setError] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const fetchPost = async () => {
            try {
                const authHeader = localStorage.getItem('username') && localStorage.getItem('password')
                    ? `Basic ${btoa(`${localStorage.getItem('username')}:${localStorage.getItem('password')}`)}`
                    : `Basic ${btoa(':')}`;

                const headers = { 'Authorization': authHeader };
                setIsAuthenticated(!!localStorage.getItem('username'));

                const response = await api.get(`/users/${username}/posts/${post_id}`, { headers });

                if (!response || !response.data) {
                    throw new Error('No data received.');
                }

                setPost(response.data);
            } catch (err) {
                if (err.response && err.response.status === 404) {
                    setError('Post not found or invalid username/post_id.');
                } else {
                    setError('An error occurred while fetching the post.');
                }
            }
        };

        fetchPost();
    }, [username, post_id]);

    if (error) {
        return <div className="error-message">{error}</div>;
    }

    if (!post) {
        return <div>Loading...</div>;
    }

    return (
        <div className="post-page-container">
            <h1 className="post-title">{post.content}</h1>
            <p className="post-author">
                <strong>Author:</strong> {post.author.full_name} ({post.author.username})
            </p>
            <p className="post-meta">
                <strong>Created At:</strong> {new Date(post.created_at).toLocaleString()}
            </p>
            <p className="post-likes">
                <strong>Likes:</strong> {post.likes}
            </p>
            {isAuthenticated && (
                <p className="post-liked">
                    {post.is_liked ? 'You liked this post.' : 'You have not liked this post.'}
                </p>
            )}
        </div>
    );
};

export default PostPage;
