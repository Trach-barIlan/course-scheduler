import React from 'react';
import Dashboard from '../components/Dashboard/Dashboard';
import '../styles/HomePage.css';

const HomePage = ({ user, onQuickAction }) => {
  return (
    <div className="home-page">
      <Dashboard user={user} onQuickAction={onQuickAction} />
    </div>
  );
};

export default HomePage;