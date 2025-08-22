import React, { useState } from "react";
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import SaveScheduleModal from './SaveScheduleModal/SaveScheduleModal';
import NotImplementedModal from './NotImplementedModal/NotImplementedModal';
import ScheduleSkeletonLoader from './SkeletonLoader/ScheduleSkeletonLoader';
import { getCached, setCached, setScheduleDetail } from '../utils/cache'; // עדכן נתיב יחסי אם צריך
import "../styles/WeeklyScheduler.css";

const WeeklySchedule = ({ schedule, isLoading, user, authToken, scheduleName, scheduleId }) => {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [selectedClass, setSelectedClass] = useState(null);
  const [highlightedCourse, setHighlightedCourse] = useState(null); // For highlighting all slots of a course
  const [draggedClass, setDraggedClass] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [currentSchedule, setCurrentSchedule] = useState(schedule);
  const [originalCourseOptions, setOriginalCourseOptions] = useState(null);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [showNotImplemented, setShowNotImplemented] = useState(false);
  const [notImplementedFeature, setNotImplementedFeature] = useState('');
  
  // Progress tracking state - only for new generation, not loaded schedules
  const [progress, setProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL

  // Update current schedule when prop changes
  React.useEffect(() => {
    setCurrentSchedule(schedule);
    // Extract original course options from the initial schedule
    if (schedule && !originalCourseOptions) {
      extractOriginalOptions(schedule);
    }
  }, [schedule, originalCourseOptions]);

  // Simulate progress tracking ONLY when loading NEW schedules (not loaded ones)
  React.useEffect(() => {
    // Only show loading animation for NEW schedule generation, not for loaded schedules
    if (isLoading && !scheduleName) {
      setProgress(0);
      setEstimatedTime(8); // 8 seconds estimated
      setCurrentStep('Analyzing course options...');
      
      const steps = [
        { progress: 15, step: 'Analyzing course options...', duration: 1000 },
        { progress: 35, step: 'Processing constraints...', duration: 1500 },
        { progress: 55, step: 'Finding valid combinations...', duration: 2000 },
        { progress: 75, step: 'Optimizing schedule...', duration: 2000 },
        { progress: 90, step: 'Finalizing layout...', duration: 1000 },
        { progress: 100, step: 'Complete!', duration: 500 }
      ];
      
      let currentStepIndex = 0;
      let totalElapsed = 0;
      
      const updateProgress = () => {
        if (currentStepIndex < steps.length && isLoading && !scheduleName) {
          const step = steps[currentStepIndex];
          setProgress(step.progress);
          setCurrentStep(step.step);
          
          totalElapsed += step.duration;
          const remaining = Math.max(0, 8 - (totalElapsed / 1000));
          setEstimatedTime(remaining);
          
          setTimeout(() => {
            currentStepIndex++;
            updateProgress();
          }, step.duration);
        }
      };
      
      updateProgress();
    } else {
      setProgress(0);
      setEstimatedTime(0);
      setCurrentStep('');
    }
  }, [isLoading, scheduleName]);

  // Extract original course options from the backend data
  const extractOriginalOptions = async (scheduleData) => {
    try {
      // We need to get the original course data that was sent to generate this schedule
      // For now, we'll store it in localStorage when the schedule is generated
      const storedOptions = localStorage.getItem('originalCourseOptions');
      if (storedOptions) {
        setOriginalCourseOptions(JSON.parse(storedOptions));
      }
    } catch (error) {
      console.error('Error extracting original options:', error);
    }
  };

  const handleNotImplementedClick = (feature) => {
    setNotImplementedFeature(feature);
    setShowNotImplemented(true);
  };

  const handleSaveSchedule = async () => {
    console.log('Save schedule clicked, user:', user);
    
    if (!user) {
      alert('Please sign in to save schedules. Click the "Sign In" button in the top navigation to create an account or log in.');
      return;
    }
    
    if (!currentSchedule || currentSchedule.length === 0) {
      alert('No schedule to save. Please generate a schedule first.');
      return;
    }
    
    // Verify authentication before opening modal
    try {
      console.log('🔍 Verifying authentication before opening save modal...');
      const authCheck = await fetch(API_BASE_URL + '/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        }
      });

      console.log('Auth check response:', authCheck.status);

      if (!authCheck.ok) {
        console.log('❌ Auth check failed, user may need to sign in again');
        alert('Your session has expired. Please refresh the page and sign in again.');
        return;
      }

      const authData = await authCheck.json();
      console.log('✅ Authentication verified for user:', authData.user?.username);

      console.log('Opening save modal with schedule:', currentSchedule);
      setShowSaveModal(true);
    } catch (error) {
      console.error('❌ Error checking authentication:', error);
      alert('Unable to verify authentication. Please refresh the page and try again.');
    }
  };

  const handleScheduleSaved = (savedSchedule) => {
    // Close the modal
    setShowSaveModal(false);
    
    // Show success message
    alert(`Schedule "${savedSchedule.schedule_name}" saved successfully!`);
    
    // Update cached schedules list
    try {
      if (user?.id) {
        // עדכון רשימת summary
        const key = 'saved_schedules_list';
        const existing = getCached(key, user.id) || [];
        const newSummary = {
          id: savedSchedule.id,
          name: savedSchedule.schedule_name,
          courseCount: savedSchedule.schedule_data?.length || 0,
          created: savedSchedule.created_at,
          status: 'active'
        };
        const updatedSummaries = [
          newSummary,
          ...existing.filter(s => s.id !== newSummary.id)
        ].slice(0, 20);
        setCached(key, user.id, updatedSummaries, 5 * 60 * 1000);

        // עדכון detail cache
        setScheduleDetail(user.id, savedSchedule.id, {
          id: savedSchedule.id,
          schedule_name: savedSchedule.schedule_name,
          schedule_data: savedSchedule.schedule_data,
          original_course_options: savedSchedule.original_course_options || [],
          created_at: savedSchedule.created_at
        });
      }
    } catch {}
  };

  // Show loading skeleton ONLY for NEW schedule generation, not loaded schedules
  if (isLoading && !scheduleName) {
    return (
      <ScheduleSkeletonLoader 
        progress={progress}
        estimatedTime={estimatedTime}
        currentStep={currentStep}
      />
    );
  }

  if (!currentSchedule || currentSchedule.length === 0) {
    return (
      <div className="weekly-scheduler-container">
        <div className="empty-state">
          <div className="empty-state-icon">📅</div>
          <h3 className="empty-state-title">No Schedule Generated</h3>
          <p className="empty-state-description">
            Fill in your course information and constraints, then click "Generate Schedule" to see your personalized weekly schedule here.
          </p>
        </div>
      </div>
    );
  }

  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  
  // Extended time range from 7 AM to 10 PM to accommodate all possible class times
  const hours = Array.from({ length: 15 }, (_, i) => i + 7); // 7 AM to 9 PM (22:00)
  
  const slots = {};
  const colors = {};

  // Enhanced color palette with better contrast and accessibility
  const predefinedColors = [
    "#3B82F6", // Blue
    "#10B981", // Emerald
    "#F59E0B", // Amber
    "#EF4444", // Red
    "#8B5CF6", // Violet
    "#06B6D4", // Cyan
    "#F97316", // Orange
    "#84CC16", // Lime
    "#EC4899", // Pink
    "#6366F1", // Indigo
  ];

  let colorIndex = 0;

  // Parse schedule and create slots
  currentSchedule.forEach(({ name, lecture, ta }, courseIndex) => {
    if (!colors[name]) {
      colors[name] = predefinedColors[colorIndex % predefinedColors.length];
      colorIndex++;
    }

    // Parse lecture slot
    const lectureMatch = typeof lecture === "string" ? lecture.match(/^(\w+)\s+(\d+)-(\d+)$/) : null;
    if (lectureMatch) {
      const [, day, start, end] = lectureMatch;
      const startHour = parseInt(start);
      const endHour = parseInt(end);
      const key = `${day}-${startHour}-${endHour}`;
      
      slots[key] = {
        text: `${name} (Lecture)`,
        color: colors[name],
        start: startHour,
        end: endHour,
        courseName: name,
        type: "Lecture",
        time: `${startHour}:00 - ${endHour}:00`,
        day: day,
        slotKey: key,
        courseIndex: courseIndex,
        isLecture: true
      };
    }

    // Parse TA slot
    const taMatch = typeof ta === "string" ? ta.match(/^(\w+)\s+(\d+)-(\d+)$/) : null;
    if (taMatch) {
      const [, day, start, end] = taMatch;
      const startHour = parseInt(start);
      const endHour = parseInt(end);
      const key = `${day}-${startHour}-${endHour}`;
      
      slots[key] = {
        text: `${name} (TA)`,
        color: colors[name],
        start: startHour,
        end: endHour,
        courseName: name,
        type: "TA Session",
        time: `${startHour}:00 - ${endHour}:00`,
        day: day,
        slotKey: key,
        courseIndex: courseIndex,
        isLecture: false
      };
    }
  });

  const parseTimeSlot = (timeSlotStr) => {
    const match = timeSlotStr.match(/^(\w+)\s+(\d+)-(\d+)$/);
    if (match) {
      const [, day, start, end] = match;
      return {
        day,
        start: parseInt(start),
        end: parseInt(end)
      };
    }
    return null;
  };

  const findAvailableSlots = (classToMove) => {
    const available = [];
    
    // Get original course options from localStorage
    const storedOptions = localStorage.getItem('originalCourseOptions');
    if (storedOptions) {
      const originalOptions = JSON.parse(storedOptions);
      const course = originalOptions.find(c => c.name === classToMove.courseName);
      
      if (course) {
        // Get the alternative time slots for this specific class type
        const alternativeSlots = classToMove.isLecture ? course.lectures : course.ta_times;
        
        // Parse each alternative slot
        alternativeSlots.forEach(slotStr => {
          const parsedSlot = parseTimeSlot(slotStr.trim());
          if (parsedSlot) {
            // Check if this slot conflicts with any other classes (except the one being moved)
            const hasConflict = Object.values(slots).some(existingSlot => {
              if (existingSlot.slotKey === classToMove.slotKey) return false; // Skip the slot being moved
              
              return existingSlot.day === parsedSlot.day && 
                     parsedSlot.start < existingSlot.end && 
                     parsedSlot.end > existingSlot.start;
            });
            
            if (!hasConflict) {
              available.push({
                day: parsedSlot.day,
                start: parsedSlot.start,
                end: parsedSlot.end,
                key: `${parsedSlot.day}-${parsedSlot.start}-${parsedSlot.end}`,
                isOriginalOption: true,
                originalSlotString: slotStr.trim()
              });
            }
          }
        });
      }
    }
    
    // If no original options found, fall back to finding any available slots
    if (available.length === 0) {
      const duration = classToMove.end - classToMove.start;
      
      // Get all currently occupied time ranges except the one being moved
      const occupiedRanges = Object.values(slots)
        .filter(slot => slot.slotKey !== classToMove.slotKey)
        .map(slot => ({
          day: slot.day,
          start: slot.start,
          end: slot.end
        }));
      
      // Check each day and time slot (extended range)
      days.forEach(day => {
        for (let startHour = 7; startHour <= 22 - duration; startHour++) { // 7 AM to 10 PM
          const endHour = startHour + duration;
          let canPlace = true;
          
          // Check if this time slot conflicts with any existing classes
          for (const occupied of occupiedRanges) {
            if (occupied.day === day) {
              // Check for overlap: new slot overlaps if it starts before occupied ends and ends after occupied starts
              if (startHour < occupied.end && endHour > occupied.start) {
                canPlace = false;
                break;
              }
            }
          }
          
          if (canPlace) {
            available.push({
              day,
              start: startHour,
              end: endHour,
              key: `${day}-${startHour}-${endHour}`,
              isOriginalOption: false
            });
          }
        }
      });
    }
    
    return available;
  };

  const handleClassClick = (slot) => {
    // If we're in drag mode and clicking the same class, cancel drag mode
    if (draggedClass && draggedClass.slotKey === slot.slotKey) {
      setDraggedClass(null);
      setAvailableSlots([]);
      setHighlightedCourse(null);
      return;
    }
    
    // If we're in drag mode and clicking a different class, switch to new class
    if (draggedClass && draggedClass.slotKey !== slot.slotKey) {
      setDraggedClass(slot);
      const availableSlots = findAvailableSlots(slot);
      setAvailableSlots(availableSlots);
      setHighlightedCourse(slot.courseName);
      console.log('Available slots for', slot.text, ':', availableSlots);
      return;
    }

    // If clicking the same course that's already highlighted, toggle off
    if (highlightedCourse === slot.courseName) {
      setHighlightedCourse(null);
      return;
    }

    // Otherwise, highlight all sessions of this course
    setHighlightedCourse(slot.courseName);
    console.log('Highlighting all sessions for course:', slot.courseName);
  };

  const handleSlotDrop = (targetSlot) => {
    if (!draggedClass) return;

    console.log('Dropping', draggedClass.text, 'to', targetSlot);

    // Update the schedule
    const newSchedule = [...currentSchedule];
    const courseIndex = draggedClass.courseIndex;
    const course = newSchedule[courseIndex];
    
    const newTimeSlot = targetSlot.originalSlotString || `${targetSlot.day} ${targetSlot.start}-${targetSlot.end}`;
    
    if (draggedClass.isLecture) {
      course.lecture = newTimeSlot;
    } else {
      course.ta = newTimeSlot;
    }
    
    setCurrentSchedule(newSchedule);
    setDraggedClass(null);
    setAvailableSlots([]);
  };

  const isSlotAvailable = (day, hour) => {
    return availableSlots.some(slot => 
      slot.day === day && hour >= slot.start && hour < slot.end
    );
  };

  const getAvailableSlotForHour = (day, hour) => {
    return availableSlots.find(slot => 
      slot.day === day && hour >= slot.start && hour < slot.end
    );
  };

  const closePopup = () => {
    setSelectedClass(null);
  };

  const cancelDragMode = () => {
    setDraggedClass(null);
    setAvailableSlots([]);
    setHighlightedCourse(null);
  };

  // Check if a course slot should be highlighted
  const isCourseHighlighted = (slot) => {
    return highlightedCourse && slot.courseName === highlightedCourse;
  };

  // Add double-click handler to start drag mode
  const handleClassDoubleClick = (slot) => {
    // Start drag mode on double-click
    setDraggedClass(slot);
    const availableSlots = findAvailableSlots(slot);
    setAvailableSlots(availableSlots);
    setHighlightedCourse(slot.courseName);
    console.log('Drag mode started for', slot.text, ':', availableSlots);
  };

  const downloadPDF = async () => {
    if (!user) {
      alert('Please sign in to download schedules. Click the "Sign In" button in the top navigation to create an account or log in.');
      return;
    }
    setIsGeneratingPDF(true);
    
    try {
      const containerElement = document.querySelector(".weekly-scheduler-container");
      
      // Temporarily hide non-essential elements
      const elementsToHide = document.querySelectorAll('.scheduler-actions, .constraints-display, .enhanced-view-section');
      elementsToHide.forEach(el => el.style.display = 'none');
      
      const canvas = await html2canvas(containerElement, { 
        scale: 1.5, // Good quality
        useCORS: true,
        backgroundColor: '#ffffff',
        scrollX: 0,
        scrollY: 0,
        width: Math.max(containerElement.scrollWidth, 1100), // Force minimum width
        height: Math.max(containerElement.scrollHeight, 800), // Force minimum height
        allowTaint: false,
        removeContainer: false,
        logging: false,
        pixelRatio: 1,
        windowWidth: Math.max(containerElement.scrollWidth, 1100),
        windowHeight: Math.max(containerElement.scrollHeight, 800),
        imageTimeout: 15000,
        onclone: (clonedDoc) => {
          // Make the table wider during capture
          const style = clonedDoc.createElement('style');
          style.textContent = `
            .scheduler-actions, .constraints-display, .enhanced-view-section { display: none !important; }
            .weekly-scheduler-container { 
              padding: 20px !important; 
              background: #ffffff !important;
              box-shadow: none !important;
              border: none !important;
              min-width: 1050px !important; /* Force wider container */
              width: 1050px !important;
              opacity: 1 !important;
            }
            #schedule-table { 
              font-size: 16px !important; 
              width: 1000px !important; /* Much wider table */
              min-width: 1000px !important;
              border-collapse: collapse !important;
              background: #ffffff !important;
              font-weight: 600 !important;
              opacity: 1 !important;
            }
            #schedule-table th, #schedule-table td { 
              padding: 18px 15px !important; 
              border: 2px solid #000000 !important;
              word-wrap: break-word !important;
              font-size: 15px !important;
              min-height: 50px !important;
              font-weight: 700 !important;
              opacity: 1 !important;
            }
            #schedule-table th {
              background: #d1ecf1 !important;
              font-weight: 900 !important;
              color: #000000 !important;
              opacity: 1 !important;
            }
            #schedule-table td:empty,
            #schedule-table td:not([style*="background-color"]) {
              background: #ffffff !important;
              color: #000000 !important;
              opacity: 1 !important;
            }
            #schedule-table td[style*="background-color"] {
              font-weight: 900 !important;
              border: 2px solid #000000 !important;
              opacity: 1 !important;
              color: #000000 !important;
              text-shadow: none !important;
            }
          `;
          clonedDoc.head.appendChild(style);
        }
      });
      
      // Restore hidden elements
      elementsToHide.forEach(el => el.style.display = '');
      
      // Use PNG with no compression for maximum quality
      const imgData = canvas.toDataURL("image/png", 1.0);
      const pdf = new jsPDF("portrait", "mm", "a4"); // Changed to portrait orientation
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      
      // No header text - use full page for schedule
      const margin = 3; // Even smaller margins for maximum width
      const availableWidth = pdfWidth - (2 * margin);
      const availableHeight = pdfHeight - (2 * margin);
      
      // Calculate proper sizing - prioritize width usage
      const canvasAspectRatio = canvas.width / canvas.height;
      
      let imgWidth, imgHeight;
      
      // Always try to use maximum width first
      imgWidth = availableWidth;
      imgHeight = availableWidth / canvasAspectRatio;
      
      // If height exceeds available space, then scale down
      if (imgHeight > availableHeight) {
        imgHeight = availableHeight;
        imgWidth = availableHeight * canvasAspectRatio;
      }
      
      // Center the schedule on the page
      const x = (pdfWidth - imgWidth) / 2;
      const y = (pdfHeight - imgHeight) / 2; 
      
      pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);
      pdf.save("WeeklySchedule.pdf");
    } catch (error) {
      console.error("Error generating PDF:", error);
      alert("Failed to generate PDF. Please try again later.");
    } finally {
      setIsGeneratingPDF(false);
    }
  };
  
  const shareTableAsImage = async () => {
    setIsSharing(true);
    
    try {
      const tableElement = document.getElementById("schedule-table");
      const canvas = await html2canvas(tableElement, { 
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff'
      });
      
      const imgData = canvas.toDataURL("image/png");
      
      if (navigator.share) {
        // Use native sharing if available
        const blob = await (await fetch(imgData)).blob();
        const file = new File([blob], "schedule.png", { type: "image/png" });
        
        await navigator.share({
          title: "My Weekly Schedule",
          text: "Check out my weekly course schedule!",
          files: [file]
        });
      } else {
        // Fallback to WhatsApp Web
        const whatsappUrl = `https://wa.me/?text=Check%20out%20my%20weekly%20schedule!`;
        window.open(whatsappUrl, "_blank");
      }
    } catch (error) {
      console.error("Error sharing:", error);
      // Fallback to simple WhatsApp link
      const whatsappUrl = `https://wa.me/?text=Check%20out%20my%20weekly%20schedule!`;
      window.open(whatsappUrl, "_blank");
    } finally {
      setIsSharing(false);
    }
  };

  // Format time display for better readability
  const formatTimeDisplay = (hour) => {
    if (hour === 0) return "12:00 AM";
    if (hour < 12) return `${hour}:00 AM`;
    if (hour === 12) return "12:00 PM";
    return `${hour - 12}:00 PM`;
  };

  return (
    <div className="weekly-scheduler-container">
      <div className="scheduler-header">
        <div className="header-content">
          <h2 className="scheduler-title">
            {scheduleName ? scheduleName : 'Weekly Schedule'}
          </h2>
          {scheduleName && (
            <div className="schedule-source">
              <div className="source-info">
                <span className="source-badge">📂 Loaded Schedule</span>
                <span className="edit-hint">You can modify course times on the left and regenerate, or you can double click a class to move it</span>
              </div>
            </div>
          )}
        </div>
        <div className="scheduler-actions">
          {(draggedClass || highlightedCourse) && (
            <button 
              onClick={cancelDragMode}
              className="action-button button-cancel"
            >
              {draggedClass ? 'Cancel Move' : 'Clear Highlight'}
            </button>
          )}
          <button 
            onClick={handleSaveSchedule}
            className="action-button button-save"
            title={!user ? "Sign in to save schedules" : "Save this schedule"}
          >
            💾 Save Schedule
          </button>
          <button 
            onClick={() => handleNotImplementedClick('export-calendar')}
            className="action-button button-calendar"
          >
            📅 Export to Calendar
          </button>
          <button 
            onClick={downloadPDF} 
            className="action-button button-download"
            disabled={isGeneratingPDF}
          >
            {isGeneratingPDF ? (
              <>
                <div className="loading-spinner"></div>
                Generating...
              </>
            ) : (
              <>
                📄 Download PDF
              </>
            )}
          </button>
          <button 
            onClick={shareTableAsImage} 
            className="action-button button-share"
            disabled={isSharing}
          >
            {isSharing ? (
              <>
                <div className="loading-spinner"></div>
                Sharing...
              </>
            ) : (
              <>
                📱 Share
              </>
            )}
          </button>
        </div>
      </div>

      {draggedClass && (
        <div className="drag-mode-info">
          <p>🔄 Moving: <strong>{draggedClass.text}</strong></p>
          <p>
            {availableSlots.some(slot => slot.isOriginalOption) 
              ? "Click on a highlighted time slot to switch to an alternative option for this class."
              : "Click on a highlighted time slot to move the class there, or click \"Cancel Move\" to exit."
            }
          </p>
        </div>
      )}

      {highlightedCourse && !draggedClass && (
        <div className="highlight-mode-info">
          <p>✨ Highlighting all sessions for: <strong>{highlightedCourse}</strong></p>
          <p>Double-click any session to move it, or click another course to highlight it instead.</p>
        </div>
      )}
      
      <div className="table-container">
        <table id="schedule-table">
          <thead>
            <tr>
              <th>Time</th>
              {days.map((d) => (
                <th key={d}>{d}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {hours.map((h) => (
              <tr key={h}>
                <td>{formatTimeDisplay(h)} - {formatTimeDisplay(h + 1)}</td>
                {days.map((d) => {
                  // Find if there's a class slot that occupies this cell
                  const occupyingSlot = Object.values(slots).find(slot => 
                    slot.day === d && h >= slot.start && h < slot.end
                  );

                  const isAvailable = isSlotAvailable(d, h);
                  const availableSlot = getAvailableSlotForHour(d, h);

                  if (occupyingSlot) {
                    const isStartHour = h === occupyingSlot.start;
                    const isDragging = draggedClass && draggedClass.slotKey === occupyingSlot.slotKey;
                    const isHighlighted = isCourseHighlighted(occupyingSlot);
                    
                    return isStartHour ? (
                      <td 
                        key={d} 
                        rowSpan={occupyingSlot.end - occupyingSlot.start} 
                        style={{ 
                          backgroundColor: occupyingSlot.color,
                          opacity: isHighlighted ? 1 : (highlightedCourse ? 0.3 : 1),
                          transform: isDragging ? 'scale(0.95)' : 'scale(1)',
                          transition: 'all 0.2s ease'
                        }}
                        title={`${occupyingSlot.text} - Click to highlight all sessions, Double-click to move`}
                        onClick={() => handleClassClick(occupyingSlot)}
                        onDoubleClick={() => handleClassDoubleClick(occupyingSlot)}
                        className={`clickable-cell ${isDragging ? 'dragging' : ''} ${isHighlighted ? 'highlighted-course' : ''}`}
                      >
                        <div className="class-content">
                          {occupyingSlot.text}
                          {isHighlighted && <span className="highlight-indicator">✨</span>}
                          {isDragging && <span className="drag-indicator">🔄</span>}
                        </div>
                      </td>
                    ) : null;
                  }

                  if (isAvailable && availableSlot) {
                    const isStartOfAvailableSlot = h === availableSlot.start;
                    return isStartOfAvailableSlot ? (
                      <td 
                        key={d}
                        rowSpan={availableSlot.end - availableSlot.start}
                        className={`available-slot ${availableSlot.isOriginalOption ? 'original-option' : ''}`}
                        onClick={() => handleSlotDrop(availableSlot)}
                        title={availableSlot.isOriginalOption 
                          ? `Switch to alternative: ${availableSlot.originalSlotString || `${availableSlot.day} ${availableSlot.start}-${availableSlot.end}`}`
                          : `Move ${draggedClass?.text} here`
                        }
                      >
                        <div className="available-slot-content">
                          <span className="move-here-text">
                            {availableSlot.isOriginalOption ? 'Switch Here' : 'Move Here'}
                          </span>
                        </div>
                      </td>
                    ) : null;
                  }

                  return <td key={d}></td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Class Details Popup */}
      {selectedClass && (
        <div className="popup-overlay" onClick={closePopup}>
          <div className="popup-content" onClick={(e) => e.stopPropagation()}>
            <div className="popup-header">
              <h3>{selectedClass.courseName}</h3>
              <button className="close-button" onClick={closePopup}>×</button>
            </div>
            <div className="popup-body">
              <div className="detail-item">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{selectedClass.type}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Day:</span>
                <span className="detail-value">{selectedClass.day}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Time:</span>
                <span className="detail-value">{selectedClass.time}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Duration:</span>
                <span className="detail-value">{selectedClass.end - selectedClass.start} hour(s)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Save Schedule Modal */}
      <SaveScheduleModal
        isOpen={showSaveModal}
        onClose={() => setShowSaveModal(false)}
        onSave={handleScheduleSaved}
        schedule={currentSchedule}
        user={user}
        authToken={authToken}
        courses={originalCourseOptions}
      />

      {/* Not Implemented Modal */}
      <NotImplementedModal
        isOpen={showNotImplemented}
        onClose={() => setShowNotImplemented(false)}
        feature={notImplementedFeature}
      />
    </div>
  );
};

export default WeeklySchedule;