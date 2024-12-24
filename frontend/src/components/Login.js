import React, { useState } from 'react';
import api from '../services/api';  
import "../styles/Login.css";

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            localStorage.setItem("username", username);
            localStorage.setItem("password", password);

            const credentials = btoa(`${username}:${password}`);

            const response = await api.get("/me", {
                headers: {
                    Authorization: `Basic ${credentials}`,
                },
            });

            
            if (response.status === 200) {
                window.location.href = '/me'; 
            }
        } catch (error) {
            setError("Невірне ім'я користувача або пароль");
            console.error("Помилка при вході:", error);
        }
    };

    return (
        <div className="login-container">
            <div className='login-card'>
                <h1>Вхід</h1>
                {error && <p className='error'>{error}</p>}
                <form onSubmit={handleSubmit} className='form-group'>
                    <div>
                        <label htmlFor="username">Ім'я користувача:</label>
                        <input
                            type="text"
                            id="username"
                            value={username}
                            required
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div>
                        <label htmlFor="password">Пароль:</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            required
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button type="submit" className='login-btn'>Увійти</button>
                </form>
            </div>
        </div>
    );
};

export default Login;
