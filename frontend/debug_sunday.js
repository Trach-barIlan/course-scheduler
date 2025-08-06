// Debug test for Sunday schedule parsing
// Paste this in browser console when looking at a generated schedule

console.log("Testing Sunday schedule parsing...");

// Test data that should include Sunday
const testSchedule = [
  { name: "Test Course", lecture: "Sun 9-11", ta: null }
];

console.log("Test schedule:", testSchedule);

// Test the parsing logic
testSchedule.forEach(({ name, lecture, ta }) => {
  console.log(`Processing course: ${name}`);
  console.log(`Lecture slot: "${lecture}"`);
  
  const lectureMatch = typeof lecture === "string" ? lecture.match(/^(\w+)\s+(\d+)-(\d+)$/) : null;
  if (lectureMatch) {
    const [, day, start, end] = lectureMatch;
    console.log(`✅ Parsed lecture: Day=${day}, Start=${start}, End=${end}`);
  } else {
    console.log(`❌ Failed to parse lecture: "${lecture}"`);
  }
});

// Check if the current schedule has Sunday courses
if (typeof currentSchedule !== 'undefined') {
  console.log("Current schedule data:", currentSchedule);
  
  currentSchedule.forEach(course => {
    if (course.lecture && course.lecture.includes('Sun')) {
      console.log("Found Sunday lecture:", course);
    }
    if (course.ta && course.ta.includes('Sun')) {
      console.log("Found Sunday TA:", course);
    }
  });
} else {
  console.log("currentSchedule not available in this context");
}
