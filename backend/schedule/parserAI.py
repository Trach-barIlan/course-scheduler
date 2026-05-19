import re
from ai_model.gliner_parser import GlinerParser

# Initialize GLiNER parser for better constraint parsing
print("🔍 PARSER AI: Initializing GlinerParser...")
try:
    constraint_parser = GlinerParser()
    PARSER_AVAILABLE = True
    print("🔍 PARSER AI: GlinerParser initialized successfully")
except Exception as e:
    PARSER_AVAILABLE = False
    print(f"❌ PARSER AI: GlinerParser initialization failed: {e}")
    import traceback
    print(f"❌ PARSER AI: Full traceback: {traceback.format_exc()}")

def parse_course_text(text):
    """Parse natural language course descriptions into structured data."""
    print(f"🔍 PARSER AI: parse_course_text called with text: '{text}'")
    print(f"🔍 PARSER AI: PARSER_AVAILABLE: {PARSER_AVAILABLE}")
    
    courses = []
    constraints = []
    
    # Use hybrid parser for constraints if available
    if PARSER_AVAILABLE:
        print("🔍 PARSER AI: Using hybrid parser for constraints...")
        try:
            constraint_result = constraint_parser.parse(text)
            constraints = constraint_result.get("constraints", [])
            print(f"🔍 PARSER AI: Hybrid parser succeeded, found {len(constraints)} constraints: {constraints}")
        except Exception as e:
            print(f"❌ PARSER AI: Hybrid parser failed: {e}")
            import traceback
            print(f"❌ PARSER AI: Full traceback: {traceback.format_exc()}")
            print("🔍 PARSER AI: Falling back to regex parsing...")
            constraints = _parse_constraints_fallback(text)
    else:
        print("🔍 PARSER AI: Using fallback regex parsing...")
        constraints = _parse_constraints_fallback(text)
    
    # Parse course information (existing logic)
    print("🔍 PARSER AI: Parsing courses...")
    courses = _parse_courses(text)
    print(f"🔍 PARSER AI: Found {len(courses)} courses: {courses}")
    
    result = {
        "courses": courses,
        "constraints": constraints
    }
    print(f"🔍 PARSER AI: Final result: {result}")
    return result

def _parse_constraints_fallback(text):
    """Fallback constraint parsing using original regex method"""
    print(f"🔍 PARSER AI FALLBACK: Starting fallback constraint parsing for: '{text}'")
    constraints = []
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    print(f"🔍 PARSER AI FALLBACK: Split into {len(sentences)} sentences: {sentences}")
    
    for i, sentence in enumerate(sentences):
        print(f"🔍 PARSER AI FALLBACK: Processing sentence {i+1}: '{sentence}'")
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