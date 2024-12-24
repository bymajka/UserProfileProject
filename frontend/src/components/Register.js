import React, { useState } from 'react';
import api from '../services/api';
import "../styles/Register.css";

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            // Надсилаємо дані для реєстрації нового користувача
            const response = await api.post("/register", {
                username,
                password,
            });

            if (response.status === 201) {
                localStorage.setItem("username", username);
                localStorage.setItem("password", password);

                const credentials = btoa(`${username}:${password}`);

                window.location.href = '/me'; 
            }
        } catch (error) {
            setError("Помилка при реєстрації. Спробуйте ще раз.");
            console.error("Помилка при реєстрації:", error);
        }
    };

    return (
        <div className='register-container'>
            <div className="register-card">
                <h1>Реєстрація</h1>
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
                    <button type="submit" className='register-btn'>Зареєструватися</button>
                </form>
            </div>
        </div>
    );
};

export default Register;
