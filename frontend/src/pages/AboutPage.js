import React from 'react';
import '../styles/AboutPage.css';

const AboutPage = () => {
  return (
    <div className="about-page">
      <div className="about-container">
        <div className="about-header">
          <h1 className="about-title">About Schedgic</h1>
          <p className="about-subtitle">
            Revolutionizing academic planning with AI-powered scheduling
          </p>
        </div>

        <div className="about-content">
          <div className="about-section">
            <div className="section-icon">🤖</div>
            <h2>AI-Powered Intelligence</h2>
            <p>
              Our advanced natural language processing understands your scheduling preferences 
              in plain English. Simply tell us "No classes before 9am" or "Avoid Tuesday mornings" 
              and our AI will optimize your schedule accordingly.
            </p>
          </div>

          <div className="about-section">
            <div className="section-icon">⚡</div>
            <h2>Lightning Fast</h2>
            <p>
              Generate optimal schedules in seconds, not hours. Our sophisticated algorithms 
              consider thousands of possible combinations to find the perfect arrangement 
              that meets all your constraints.
            </p>
          </div>

          <div className="about-section">
            <div className="section-icon">🎯</div>
            <h2>Conflict-Free Scheduling</h2>
            <p>
              Never worry about overlapping classes again. Our system automatically detects 
              and prevents scheduling conflicts while maximizing your preferences for 
              crammed or spaced-out schedules.
            </p>
          </div>

          <div className="about-section">
            <div className="section-icon">📱</div>
            <h2>Export & Share</h2>
            <p>
              Download your schedule as a beautiful PDF, export to your calendar app, 
              or share it with friends and advisors. Your schedule, your way.
            </p>
          </div>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <h3>🔄 Drag & Drop Editing</h3>
            <p>Easily modify your schedule by dragging classes to alternative time slots</p>
          </div>
          
          <div className="feature-card">
            <h3>💾 Save & Sync</h3>
            <p>Save multiple schedules and access them from any device</p>
          </div>
          
          <div className="feature-card">
            <h3>🎨 Beautiful Design</h3>
            <p>Clean, modern interface that makes scheduling a pleasure</p>
          </div>
          
          <div className="feature-card">
            <h3>🔒 Secure & Private</h3>
            <p>Your data is encrypted and protected with enterprise-grade security</p>
          </div>
        </div>

        <div className="team-section">
          <h2>Built for Students, by Students</h2>
          <p>
            We understand the challenges of academic planning because we've been there. 
            Schedgic was born from the frustration of manually creating schedules and 
            the desire to make this process intelligent, efficient, and enjoyable.
          </p>
          
          <div className="stats-row">
            <div className="stat">
              <div className="stat-number">Many</div>
              <div className="stat-label">Schedules Generated</div>
            </div>
            <div className="stat">
              <div className="stat-number">100%</div>
              <div className="stat-label">Success Rate</div>
            </div>
            <div className="stat">
              <div className="stat-number">Many</div>
              <div className="stat-label">Happy Students</div>
            </div>
          </div>
        </div>

        <div className="cta-section">
          <h2>Ready to Transform Your Scheduling?</h2>
          <p>Join thousands of students who have already discovered the power of AI-driven scheduling.</p>
          <button className="cta-button" onClick={() => window.location.href = '/scheduler'}>
            Get Started Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;