import React from "react";

const PostList = ({ posts, onLike, onUnlike }) => {
    console.log('Posts in PostList:', posts);

    if (!posts || posts.length === 0) {
        return <p>Немає публікацій для відображення.</p>;
    }

    return (
        <ul>
            {posts.map((post) => (
                <li key={post.id} style={{ marginBottom: '20px', listStyleType: 'none', borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>
                    <h3>{post.content}</h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <button 
                            onClick={() => (post.is_liked ? onUnlike(post.id) : onLike(post.id))}
                            style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '20px',
                                color: post.is_liked ? 'red' : 'grey',
                            }}
                        >
                            {post.is_liked ? '❤️' : '🤍'}
                        </button>
                        <span>Лайків: {post.likes}</span>
                    </div>
                </li>
            ))}
        </ul>
    );
};

export default PostList;
