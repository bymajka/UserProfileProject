import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import UserProfile from './components/UserProfile';
import UserPage from './components/UserPage';
import PostPage from './components/PostPage';
import './App.css';

const navItems = [
    { index: 1, to: "/login", label: "Вхід" },
    { index: 2, to: "/register", label: "Реєстрація" },
    { index: 3, to: "/me", label: "Моя сторінка" },
  ];

const Navigation = () => (
    <ul className='nav-list'>
        {navItems.map((item) => {
            return(
                <li key={item.index} className='nav-item'>
                    <NavLink to={item.to} className="nav-link" activeClassName="active-link">
                        {item.label}
                    </NavLink>
                </li>
            );
        })}
    </ul>
)

const App = () => {
    return (
        <Router>
            <div className="app-container">
                <header className="app-header">
                    <nav className="nav-bar">
                        <Navigation />
                    </nav>
                </header>
                <main className="main-content">
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/me" element={<UserProfile />} />
                        <Route path="/users/:username" element={<UserPage/>} />
                        <Route path="/users/:username/posts/:post_id" element={<PostPage />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
};

export default App;
