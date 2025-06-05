import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import { useLocation } from "react-router-dom";

const WeeklySchedule = () => {
  const location = useLocation();
  const schedule = location.state?.schedule;

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

  return (
    <div style={{ padding: "20px", maxWidth: "95%", margin: "0 auto", height: "70vh" }}>
      <button
        onClick={downloadPDF}
        style={{
          marginBottom: "20px",
          padding: "10px 20px",
          backgroundColor: "#007BFF",
          color: "#fff",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          fontSize: "16px",
        }}
      >
        Download as PDF
      </button>
      <table
        id="schedule-table"
        style={{
          width: "100%",
          height: "100%", // Ensure the table fills the container
          borderCollapse: "collapse",
          fontFamily: "Arial, sans-serif",
          fontSize: "18px", // Increase font size for better readability
          textAlign: "center",
        }}
      >
        <thead>
          <tr>
            <th
              style={{
                backgroundColor: "#f4f4f4",
                padding: "15px", // Increase padding for larger cells
                border: "1px solid #ddd",
                fontWeight: "bold",
              }}
            >
              Hour
            </th>
            {days.map((d) => (
              <th
                key={d}
                style={{
                  backgroundColor: "#f4f4f4",
                  padding: "15px", // Increase padding for larger cells
                  border: "1px solid #ddd",
                  fontWeight: "bold",
                }}
              >
                {d}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {hours.map((h) => (
            <tr key={h}>
              <td
                style={{
                  backgroundColor: "#f9f9f9",
                  padding: "15px", // Increase padding for larger cells
                  border: "1px solid #ddd",
                  fontWeight: "bold",
                }}
              >
                {h}:00
              </td>
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
                      style={{
                        backgroundColor: slot.color,
                        color: "#000", // Text color set to black
                        border: "1px solid #ddd",
                        padding: "15px", // Increase padding for larger cells
                        verticalAlign: "middle",
                        fontWeight: "bold",
                      }}
                    >
                      {slot.text}
                    </td>
                  ) : null; // Skip rendering for non-start hours
                }

                return (
                  <td
                    key={d}
                    style={{
                      backgroundColor: "#fff",
                      border: "1px solid #ddd",
                      padding: "15px", // Increase padding for larger cells
                    }}
                  />
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default WeeklySchedule;