import React, { useState } from "react";
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import "../styles/WeeklyScheduler.css";

const WeeklySchedule = ({ schedule, isLoading }) => {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [isSharing, setIsSharing] = useState(false);

  if (isLoading) {
    return (
      <div className="weekly-scheduler-container">
        <div className="loading-schedule">
          <div className="loading-spinner"></div>
          <p className="loading-text">Generating your schedule...</p>
        </div>
      </div>
    );
  }

  if (!schedule || schedule.length === 0) {
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

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const hours = Array.from({ length: 12 }, (_, i) => i + 8);
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

  schedule.forEach(({ name, lecture, ta }) => {
    if (!colors[name]) {
      colors[name] = predefinedColors[colorIndex % predefinedColors.length];
      colorIndex++;
    }

    [lecture, ta].forEach((slotStr, i) => {
      const [day, times] = slotStr.split(" ");
      const [start, end] = times.split("-").map(Number);
      const key = `${day}-${start}-${end}`;
      slots[key] = {
        text: `${name} ${i === 0 ? "(Lecture)" : "(TA)"}`,
        color: colors[name],
        start,
        end,
      };
    });
  });

  const downloadPDF = async () => {
    setIsGeneratingPDF(true);
    try {
      const tableElement = document.getElementById("schedule-table");
      const canvas = await html2canvas(tableElement, { 
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff'
      });
      
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("landscape", "mm", "a4");
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pdfWidth - 20;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      // Add title
      pdf.setFontSize(20);
      pdf.setTextColor(59, 130, 246); // Primary blue
      pdf.text("Weekly Course Schedule", 20, 20);

      // Add date
      pdf.setFontSize(12);
      pdf.setTextColor(107, 114, 128); // Gray
      pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 20, 30);

      if (imgHeight > pdfHeight - 40) {
        let y = 40;
        while (y < imgHeight) {
          pdf.addImage(imgData, "PNG", 10, y, imgWidth, imgHeight);
          y += pdfHeight - 40;
          if (y < imgHeight) pdf.addPage();
        }
      } else {
        pdf.addImage(imgData, "PNG", 10, 40, imgWidth, imgHeight);
      }

      pdf.save("WeeklySchedule.pdf");
    } catch (error) {
      console.error("Error generating PDF:", error);
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

  return (
    <div className="weekly-scheduler-container">
      <div className="scheduler-header">
        <h2 className="scheduler-title">Weekly Schedule</h2>
        <div className="scheduler-actions">
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
                <td>{h}:00 - {h + 1}:00</td>
                {days.map((d) => {
                  const slotKey = Object.keys(slots).find((key) => {
                    const [day, start, end] = key.split("-");
                    return day === d && h >= parseInt(start) && h < parseInt(end);
                  });

                  if (slotKey) {
                    const slot = slots[slotKey];
                    const isStartHour = h === slot.start;
                    return isStartHour ? (
                      <td 
                        key={d} 
                        rowSpan={slot.end - slot.start} 
                        style={{ backgroundColor: slot.color }}
                        title={slot.text}
                      >
                        {slot.text}
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
    </div>
  );
};

export default WeeklySchedule;