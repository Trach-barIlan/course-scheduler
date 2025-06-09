import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import "../styles/WeeklyScheduler.css";
const WeeklySchedule = ({ schedule }) => {
  if (!schedule || schedule.length === 0) {
    return <div>No schedule available</div>;
  }

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const hours = Array.from({ length: 12 }, (_, i) => i + 8);
  const slots = {};
  const colors = {};

  // Predefined colors for courses
  const predefinedColors = [
    "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF", "#33FFF5", "#F5FF33", "#FF8C33"
  ];

  let colorIndex = 0;

  schedule.forEach(({ name, lecture, ta }) => {
    if (!colors[name]) {
      // Assign a unique color for each course
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

   const downloadPDF = () => {
    const tableElement = document.getElementById("schedule-table");
    html2canvas(tableElement, { scale: 3 }).then((canvas) => {
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("portrait", "mm", "a4");
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pdfWidth - 20; // Add margins
      const imgHeight = (canvas.height * imgWidth) / canvas.width; // Maintain aspect ratio

      if (imgHeight > pdfHeight - 20) {
        // Handle large tables by splitting into multiple pages
        let y = 10;
        while (y < imgHeight) {
          pdf.addImage(imgData, "PNG", 10, y, imgWidth, imgHeight);
          y += pdfHeight - 20; // Move to the next page
          if (y < imgHeight) pdf.addPage();
        }
      } else {
        pdf.addImage(imgData, "PNG", 10, 10, imgWidth, imgHeight);
      }

      pdf.save("WeeklySchedule.pdf");
    });
  };

const shareTableAsImage = () => {
  const tableElement = document.getElementById("schedule-table");
  html2canvas(tableElement, { scale: 3 }).then((canvas) => {
    const imgData = canvas.toDataURL("image/png");

    // יצירת קישור לשיתוף בווטסאפ
    const whatsappUrl = `https://wa.me/?text=Check out my weekly schedule!`;
    const newWindow = window.open(whatsappUrl, "_blank");

    // הוספת התמונה לחלון החדש (לא ניתן לשלוח ישירות דרך API של ווטסאפ)
    if (newWindow) {
      const img = newWindow.document.createElement("img");
      img.src = imgData;
      img.style.maxWidth = "100%";
      newWindow.document.body.appendChild(img);
    }
  });
};

    return (
    <div style={{ padding: "20px", width: "100%", height: "100%" }}>
      <button onClick={downloadPDF} className="button button-download">
        Download as PDF
      </button>
      <button onClick={shareTableAsImage} className="button button-share">
        Share on WhatsApp
      </button>
      <table id="schedule-table">
        <thead>
          <tr>
            <th>Hour</th>
            {days.map((d) => (
              <th key={d}>{d}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {hours.map((h) => (
            <tr key={h}>
              <td>{h}:00</td>
              {days.map((d) => {
                const slotKey = Object.keys(slots).find((key) => {
                  const [day, start, end] = key.split("-");
                  return day === d && h >= parseInt(start) && h < parseInt(end);
                });
  
                if (slotKey) {
                  const slot = slots[slotKey];
                  const isStartHour = h === slot.start;
                  return isStartHour ? (
                    <td key={d} rowSpan={slot.end - slot.start} style={{ backgroundColor: slot.color }}>
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
  );
};

export default WeeklySchedule;