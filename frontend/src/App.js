import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import UserProfile from './components/UserProfile';
import UserPage from './components/UserPage';
import './App.css';

const App = () => {
    return (
        <Router>
            <div className="app-container">
                <header className="app-header">
                    <nav className="nav-bar">
                        <ul className="nav-list">
                            <li className="nav-item">
                                <NavLink to="/login" className="nav-link" activeClassName="active-link">
                                    Вхід
                                </NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink to="/register" className="nav-link" activeClassName="active-link">
                                    Реєстрація
                                </NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink to="/me" className="nav-link" activeClassName="active-link">
                                    Моя сторінка
                                </NavLink>
                            </li>
                        </ul>
                    </nav>
                </header>
                <main className="main-content">
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/me" element={<UserProfile />} />
                        <Route path="/users/:username" element={<UserPage/>} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
};

export default App;
