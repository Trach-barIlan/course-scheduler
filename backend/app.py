from flask import Flask, request, jsonify
from flask_cors import CORS
from schedule.logic import generate_schedule  # Remove parse_time_slot from here
from schedule.utils import parse_time_slot
from schedule.parserAI import parse_course_text
from ai_model.ml_parser import ScheduleParser

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

schedule_parser = ScheduleParser()
model_nlp = schedule_parser.nlp

def extract_hour_from_text(text):
    """Converts time expressions to 24-hour integer values."""
    text = text.strip().lower()
    
    if text in ["noon"]:
        return 12
    if text in ["midnight"]:
        return 0

    import re
    match = re.match(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
    if not match:
        return None

    hour = int(match.group(1))
    minutes = int(match.group(2)) if match.group(2) else 0
    period = match.group(3)

    if period == "pm" and hour < 12:
        hour += 12
    elif period == "am" and hour == 12:
        hour = 0

    return hour

def normalize_text(text):
    """Normalize text before NER processing."""
    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    normalized = text
    
    # Convert day names to title case
    for day in day_names:
        # Replace full lowercase version with title case
        normalized = normalized.replace(day.lower(), day.title())
        # Replace full uppercase version with title case
        normalized = normalized.replace(day.upper(), day.title())
    
    return normalized

@app.route("/api/parse", methods=["POST"])
def parse_input():
    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "Missing text input"}), 400

    text = data["text"].strip()
    # Normalize text before processing
    normalized_text = normalize_text(text)
    
    doc = model_nlp(normalized_text)

    constraints = []
    raw_entities = []

    for ent in doc.ents:
        raw_entities.append({
            "specifics": ent.text,
            "label": ent.label_
        })

        if ent.label_ == "NO_CLASS_BEFORE":
            hour = extract_hour_from_text(ent.text)
            if hour is not None:
                constraints.append({
                    "type": "No Class Before",
                    "time": hour
                })

        elif ent.label_ == "NO_CLASS_DAY":
            constraints.append({
                "type": "No Class Day",
                "day": ent.text.strip().capitalize()[:3]  # e.g., Tuesday -> Tue
            })
        elif ent.label_ == "NO_CLASS_AFTER":
            hour = extract_hour_from_text(ent.text)
            if hour is not None:
                constraints.append({
                    "type": "No Class After",
                    "time": hour
                })
        elif ent.label_ == "AVOID_TA":
            ta_name = ent.text.replace("ta", "").replace("TA", "").title().strip()
            if ta_name:
                constraints.append({
                    "type": "Avoid TA",
                    "name": ta_name
                })

    return jsonify({
        "constraints": constraints,
        "entities": raw_entities
    }), 200

@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    app.logger.debug(f"Received data: {request.json}")

    # Validate request data
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "courses" not in data:
        return jsonify({"error": "No courses provided"}), 400
    if not isinstance(data["courses"], list):
        return jsonify({"error": "Courses must be an array"}), 400
    if not data["courses"]:
        return jsonify({"error": "Empty courses array"}), 400

    preference = data.get("preference", "crammed")
    if preference not in ["crammed", "spaced"]:
        return jsonify({"error": "Invalid preference value"}), 400

    constraints = data.get("constraints", [])
    # Don't parse constraints if they're already a list
    parsed_constraints = {"constraints": constraints} if isinstance(constraints, list) else parse_course_text(constraints)

    try:

        # Validate and parse course data
        courses = []
        for i, c in enumerate(data["courses"]):
            app.logger.debug(f"Processing course {i}: {c}")

            if not isinstance(c, dict):
                return jsonify({"error": f"Invalid course format at index {i}"}), 400
            
            # Validate required fields
            if not c.get("name"):
                return jsonify({"error": f"Missing name for course at index {i}"}), 400
            if not c.get("lectures"):
                return jsonify({"error": f"Missing lectures for {c['name']}"}), 400
            if not c.get("ta_times"):
                return jsonify({"error": f"Missing TA times for {c['name']}"}), 400

            # Parse time slots (handle both string and array inputs)
            lectures = [str(l) for l in c["lectures"]] if isinstance(c["lectures"], list) else c["lectures"].split(",")
            ta_times = [str(t) for t in c["ta_times"]] if isinstance(c["ta_times"], list) else c["ta_times"].split(",")

            # Parse each time slot
            lec_slots = [parse_time_slot(s.strip()) for s in lectures if s]
            ta_slots = [parse_time_slot(s.strip()) for s in ta_times if s]

            app.logger.debug(f"Parsed lecture slots: {lec_slots}")
            app.logger.debug(f"Parsed TA slots: {ta_slots}")

            # Validate parsed slots
            if not any(lec_slots):
                return jsonify({"error": f"Invalid lecture time format for {c['name']}"}), 400
            if not any(ta_slots):
                return jsonify({"error": f"Invalid TA time format for {c['name']}"}), 400

            # Filter out None values and add to courses
            courses.append({
                "name": c["name"],
                "lectures": [s for s in lec_slots if s],
                "ta_times": [s for s in ta_slots if s]
            })

        print(f"Parsed constraints: {parsed_constraints.get("constraints") if parsed_constraints else None}")

        # Generate schedule
        schedule = generate_schedule(
            courses=courses,
            preference=preference,
            constraints=parsed_constraints.get("constraints") if parsed_constraints else None
        )

        if schedule is None:
            return jsonify({
                "error": "No valid schedule found",
                "details": "Could not find a schedule that satisfies all constraints"
            }), 200

        return jsonify({"schedule": schedule}), 200

    except Exception as e:
        app.logger.error(f"Error generating schedule: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
