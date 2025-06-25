import React, { useState } from 'react';
import './ScheduleGuide.css';

const ScheduleGuide = ({ isOpen, onClose, onStartScheduling }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: "Welcome to Schedule Creation! 🎯",
      content: (
        <div className="guide-step">
          <div className="step-icon">🚀</div>
          <h3>Let's create your perfect schedule</h3>
          <p>This guide will walk you through creating an optimized course schedule in just a few simple steps. We'll help you:</p>
          <ul>
            <li>Add your courses and available time slots</li>
            <li>Set your scheduling preferences</li>
            <li>Use AI to understand your constraints</li>
            <li>Generate and customize your schedule</li>
          </ul>
          <div className="step-tip">
            <span className="tip-icon">💡</span>
            <span>This should take about 3-5 minutes to complete</span>
          </div>
        </div>
      )
    },
    {
      title: "Step 1: Choose Your Schedule Style 📅",
      content: (
        <div className="guide-step">
          <div className="step-icon">⚖️</div>
          <h3>Pick your scheduling preference</h3>
          <p>First, you'll choose how you want your classes arranged:</p>
          
          <div className="preference-options">
            <div className="preference-card">
              <div className="preference-header">
                <span className="preference-icon">📦</span>
                <h4>Crammed Schedule</h4>
              </div>
              <p>Fewer days, back-to-back classes</p>
              <div className="preference-example">
                <strong>Example:</strong> All classes on Mon/Wed/Fri
              </div>
            </div>
            
            <div className="preference-card">
              <div className="preference-header">
                <span className="preference-icon">🌊</span>
                <h4>Spaced Out Schedule</h4>
              </div>
              <p>More days, fewer gaps between classes</p>
              <div className="preference-example">
                <strong>Example:</strong> Classes spread across Mon-Fri
              </div>
            </div>
          </div>
          
          <div className="step-tip">
            <span className="tip-icon">💡</span>
            <span>Choose based on your commute and study preferences</span>
          </div>
        </div>
      )
    },
    {
      title: "Step 2: Add Your Courses 📚",
      content: (
        <div className="guide-step">
          <div className="step-icon">📝</div>
          <h3>Enter your course information</h3>
          <p>For each course, you'll need to provide:</p>
          
          <div className="course-info-grid">
            <div className="info-item">
              <div className="info-icon">🏷️</div>
              <div className="info-content">
                <h4>Course Name</h4>
                <p>e.g., "CS101", "Mathematics", "Physics"</p>
              </div>
            </div>
            
            <div className="info-item">
              <div className="info-icon">🎓</div>
              <div className="info-content">
                <h4>Lecture Times</h4>
                <p>Available lecture slots</p>
                <div className="example">Monday 9-11, Wednesday 10-12</div>
              </div>
            </div>
            
            <div className="info-item">
              <div className="info-icon">👨‍🏫</div>
              <div className="info-content">
                <h4>TA Session Times</h4>
                <p>Available TA/tutorial slots</p>
                <div className="example">Tuesday 14-16, Thursday 15-17</div>
              </div>
            </div>
          </div>
          
          <div className="step-tip">
            <span className="tip-icon">💡</span>
            <span>You can add multiple courses and we'll find the best combination</span>
          </div>
        </div>
      )
    },
    {
      title: "Step 3: Set Your Constraints 🎯",
      content: (
        <div className="guide-step">
          <div className="step-icon">🤖</div>
          <h3>Tell us your preferences in plain English</h3>
          <p>Our AI understands natural language! You can type constraints like:</p>
          
          <div className="constraints-examples">
            <div className="constraint-example">
              <div className="constraint-icon">🌅</div>
              <div className="constraint-text">
                <strong>Time Preferences:</strong>
                <span>"No classes before 9am"</span>
                <span>"No classes after 5pm"</span>
              </div>
            </div>
            
            <div className="constraint-example">
              <div className="constraint-icon">📅</div>
              <div className="constraint-text">
                <strong>Day Preferences:</strong>
                <span>"No classes on Friday"</span>
                <span>"I can't attend Tuesday classes"</span>
              </div>
            </div>
            
            <div className="constraint-example">
              <div className="constraint-icon">👤</div>
              <div className="constraint-text">
                <strong>TA Preferences:</strong>
                <span>"Avoid TA Smith"</span>
                <span>"I prefer TA Johnson"</span>
              </div>
            </div>
          </div>
          
          <div className="step-tip">
            <span className="tip-icon">💡</span>
            <span>The more specific you are, the better we can optimize your schedule</span>
          </div>
        </div>
      )
    },
    {
      title: "Step 4: Generate & Customize 🎨",
      content: (
        <div className="guide-step">
          <div className="step-icon">⚡</div>
          <h3>Watch the magic happen</h3>
          <p>Once you click "Generate Schedule", our AI will:</p>
          
          <div className="generation-process">
            <div className="process-step">
              <div className="process-number">1</div>
              <div className="process-content">
                <h4>Parse Your Constraints</h4>
                <p>AI understands your natural language preferences</p>
              </div>
            </div>
            
            <div className="process-step">
              <div className="process-number">2</div>
              <div className="process-content">
                <h4>Find Valid Combinations</h4>
                <p>Check all possible schedule combinations</p>
              </div>
            </div>
            
            <div className="process-step">
              <div className="process-number">3</div>
              <div className="process-content">
                <h4>Optimize & Display</h4>
                <p>Show your perfect schedule in a visual calendar</p>
              </div>
            </div>
          </div>
          
          <div className="customization-info">
            <h4>🎯 Customize Further</h4>
            <p>Don't like a time slot? Simply drag and drop classes to alternative times!</p>
          </div>
          
          <div className="step-tip">
            <span className="tip-icon">💡</span>
            <span>You can save, export, or share your final schedule</span>
          </div>
        </div>
      )
    },
    {
      title: "Ready to Start? 🚀",
      content: (
        <div className="guide-step">
          <div className="step-icon">✨</div>
          <h3>You're all set!</h3>
          <p>Now you know how to create the perfect schedule. Here's what you'll do:</p>
          
          <div className="final-checklist">
            <div className="checklist-item">
              <span className="check-icon">✅</span>
              <span>Choose crammed or spaced schedule style</span>
            </div>
            <div className="checklist-item">
              <span className="check-icon">✅</span>
              <span>Add your courses with available time slots</span>
            </div>
            <div className="checklist-item">
              <span className="check-icon">✅</span>
              <span>Write your constraints in natural language</span>
            </div>
            <div className="checklist-item">
              <span className="check-icon">✅</span>
              <span>Generate and customize your schedule</span>
            </div>
            <div className="checklist-item">
              <span className="check-icon">✅</span>
              <span>Save or export your perfect schedule</span>
            </div>
          </div>
          
          <div className="success-message">
            <div className="success-icon">🎉</div>
            <p>Ready to create your first schedule? Let's make it happen!</p>
          </div>
        </div>
      )
    }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleStartScheduling = () => {
    onStartScheduling();
    onClose();
  };

  const handleClose = () => {
    setCurrentStep(0);
    onClose();
  };

  if (!isOpen) return null;

  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <div className="guide-overlay">
      <div className="guide-container">
        <div className="guide-header">
          <div className="guide-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              ></div>
            </div>
            <span className="progress-text">
              Step {currentStep + 1} of {steps.length}
            </span>
          </div>
          <button className="guide-close" onClick={handleClose}>×</button>
        </div>

        <div className="guide-content">
          <h2 className="guide-title">{steps[currentStep].title}</h2>
          {steps[currentStep].content}
        </div>

        <div className="guide-actions">
          <div className="guide-navigation">
            {!isFirstStep && (
              <button className="guide-btn guide-btn-secondary" onClick={prevStep}>
                ← Previous
              </button>
            )}
            
            <div className="step-indicators">
              {steps.map((_, index) => (
                <div 
                  key={index}
                  className={`step-dot ${index <= currentStep ? 'active' : ''}`}
                  onClick={() => setCurrentStep(index)}
                />
              ))}
            </div>
            
            {!isLastStep ? (
              <button className="guide-btn guide-btn-primary" onClick={nextStep}>
                Next →
              </button>
            ) : (
              <button className="guide-btn guide-btn-success" onClick={handleStartScheduling}>
                Start Creating! 🚀
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScheduleGuide;