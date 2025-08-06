import re
from ai_model.hybrid_parser import HybridScheduleParser

# Initialize hybrid parser for better constraint parsing
try:
    constraint_parser = HybridScheduleParser()
    PARSER_AVAILABLE = True
except Exception:
    PARSER_AVAILABLE = False

def parse_course_text(text):
    """Parse natural language course descriptions into structured data."""
    courses = []
    constraints = []
    
    # Use hybrid parser for constraints if available
    if PARSER_AVAILABLE:
        try:
            constraint_result = constraint_parser.parse(text)
            constraints = constraint_result.get("constraints", [])
        except Exception:
            constraints = _parse_constraints_fallback(text)
    else:
        constraints = _parse_constraints_fallback(text)
    
    # Parse course information (existing logic)
    courses = _parse_courses(text)
    
    return {
        "courses": courses,
        "constraints": constraints
    }

def _parse_constraints_fallback(text):
    """Fallback constraint parsing using original regex method"""
    constraints = []
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Parse time constraints
        if "no classes before" in sentence_lower or "not before" in sentence_lower:
            time_match = re.search(r'(\d{1,2})(?::\d{2})?\s*(?:am|pm)?', sentence_lower)
            if time_match:
                time = int(time_match.group(1))
                constraints.append({"type": "no_classes_before", "time": time})

        # Parse day constraints
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            if f"no classes on {day}" in sentence_lower or f"not on {day}" in sentence_lower:
                constraints.append({
                    "type": "no_day", 
                    "day": day[:3].capitalize()
                })
    
    return constraints

def _parse_courses(text):
    """Parse course information from text"""
    courses = []
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    current_course = None
    for sentence in sentences:
        sentence_lower = sentence.lower()
        
        # Skip constraint sentences
        if any(phrase in sentence_lower for phrase in ["no classes", "not before", "not after", "avoid"]):
            continue
            
        # Parse course information
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
    
    return courses