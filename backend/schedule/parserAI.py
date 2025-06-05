import re

def parse_course_text(text):
    """Parse natural language course descriptions into structured data."""
    courses = []
    constraints = []
    # Split into sentences
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    current_course = None
    for sentence in sentences:
        # Check for constraints first
        sentence_lower = sentence.lower()
        
        # Parse time constraints
        if "no classes before" in sentence_lower or "not before" in sentence_lower:
            time_match = re.search(r'(\d{1,2})(?::\d{2})?\s*(?:am|pm)?', sentence_lower)
            if time_match:
                time = int(time_match.group(1))
                constraints.append({"type": "no_early_classes", "time": time})
                continue

        # Parse day constraints
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            if f"no classes on {day}" in sentence_lower or f"not on {day}" in sentence_lower:
                constraints.append({
                    "type": "no_day", 
                    "day": day[:3].capitalize()
                })
                continue

        # If not a constraint, try to parse as course info
        course_match = re.search(r'([A-Za-z]+\s*\d+)', sentence, re.IGNORECASE)
        time_slots = re.findall(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Mon|Tue|Wed|Thu|Fri)\s*(?:or\s*(?:Monday|Tuesday|Wednesday|Thursday|Friday|Mon|Tue|Wed|Thu|Fri)\s*)*(\d{1,2})\s*-\s*(\d{1,2})', sentence, re.IGNORECASE)
        
        if course_match:
            current_course = {
                "name": course_match.group(1).strip(),
                "lectures": [],
                "ta_times": []
            }
            courses.append(current_course)
        
        if current_course and time_slots:
            is_ta = "ta" in sentence_lower or "teaching assistant" in sentence_lower
            for day, start, end in time_slots:
                days = re.findall(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Mon|Tue|Wed|Thu|Fri)', sentence, re.IGNORECASE)
                for d in days:
                    time_slot = f"{d} {start}-{end}"
                    if is_ta:
                        current_course["ta_times"].append(time_slot)
                    else:
                        current_course["lectures"].append(time_slot)
    
    return {
        "courses": courses,
        "constraints": constraints
    }