import React, { useState } from 'react';
import './ContactPage.css';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    type: 'feedback',
    message: '',
    university: '',
    course: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
      const response = await fetch(`${API_BASE_URL}/api/contact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent
        })
      });

      if (response.ok) {
        setSubmitStatus('success');
        setFormData({
          name: '',
          email: '',
          subject: '',
          type: 'feedback',
          message: '',
          university: '',
          course: ''
        });
      } else {
        throw new Error('Failed to submit form');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="contact-page">
      <div className="contact-container">
        <div className="contact-header">
          <h1>📞 Contact Us</h1>
          <p>We'd love to hear from you! Send us your feedback, bug reports, or suggestions.</p>
        </div>

        <div className="contact-content">
          <div className="contact-info">
            <h3>🚀 Help Us Improve</h3>
            <div className="info-section">
              <h4>💡 Feedback</h4>
              <p>Share your thoughts on how we can make the course scheduler better for you.</p>
            </div>
            <div className="info-section">
              <h4>🐛 Bug Reports</h4>
              <p>Found a bug? Let us know the details so we can fix it quickly.</p>
            </div>
            <div className="info-section">
              <h4>✨ Feature Requests</h4>
              <p>Have an idea for a new feature? We'd love to hear your suggestions!</p>
            </div>
            <div className="info-section">
              <h4>🏫 University Support</h4>
              <p>Need support for your university? Tell us which one and we'll consider adding it.</p>
            </div>
          </div>

          <form className="contact-form" onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="name">Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="Your name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="your.email@example.com"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="type">Type *</label>
                <select
                  id="type"
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  required
                >
                  <option value="feedback">💡 Feedback</option>
                  <option value="bug">🐛 Bug Report</option>
                  <option value="feature">✨ Feature Request</option>
                  <option value="university">🏫 University Support</option>
                  <option value="other">📝 Other</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="subject">Subject *</label>
                <input
                  type="text"
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  required
                  placeholder="Brief description of your message"
                />
              </div>
            </div>

            {(formData.type === 'bug' || formData.type === 'university') && (
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="university">University</label>
                  <input
                    type="text"
                    id="university"
                    name="university"
                    value={formData.university}
                    onChange={handleChange}
                    placeholder="Which university? (e.g., Bar-Ilan University)"
                  />
                </div>
                {formData.type === 'bug' && (
                  <div className="form-group">
                    <label htmlFor="course">Course (if applicable)</label>
                    <input
                      type="text"
                      id="course"
                      name="course"
                      value={formData.course}
                      onChange={handleChange}
                      placeholder="Course name or code (optional)"
                    />
                  </div>
                )}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="message">Message *</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                rows={6}
                placeholder={getMessagePlaceholder(formData.type)}
              />
            </div>

            {submitStatus === 'success' && (
              <div className="status-message success">
                ✅ Thank you! Your message has been sent successfully. We'll get back to you soon!
              </div>
            )}

            {submitStatus === 'error' && (
              <div className="status-message error">
                ❌ Sorry, there was an error sending your message. Please try again or contact us directly.
              </div>
            )}

            <button 
              type="submit" 
              className="submit-button"
              disabled={isSubmitting}
            >
              {isSubmitting ? '📤 Sending...' : '📨 Send Message'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

const getMessagePlaceholder = (type) => {
  switch (type) {
    case 'feedback':
      return 'Share your thoughts about the course scheduler. What do you like? What could be improved?';
    case 'bug':
      return 'Please describe the bug you encountered. Include steps to reproduce it, what you expected to happen, and what actually happened.';
    case 'feature':
      return 'Describe the feature you\'d like to see. How would it work? How would it help you?';
    case 'university':
      return 'Tell us about the university you\'d like us to support. Do you have access to their course catalog?';
    default:
      return 'Tell us how we can help you...';
  }
};

export default ContactPage;
