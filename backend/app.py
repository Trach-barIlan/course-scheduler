from flask import Flask, request, jsonify, session
from flask_cors import CORS
from schedule.logic import generate_schedule
from schedule.utils import parse_time_slot
from schedule.parserAI import parse_course_text
from ai_model.ml_parser import ScheduleParser
from auth.routes import auth_bp
from api.schedules import schedules_bp
from api.statistics import statistics_bp
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced session configuration for cross-origin requests
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow JavaScript access for debugging
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-origin cookies
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'schedgic_session'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None  # Allow cookies across different ports

# Enhanced CORS configuration with explicit cookie support
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Cookie"],
     expose_headers=["Set-Cookie"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(schedules_bp, url_prefix='/api/schedules')
app.register_blueprint(statistics_bp, url_prefix='/api/statistics')

# Initialize AI parser
try:
    schedule_parser = ScheduleParser()
    model_nlp = schedule_parser.nlp
    print("✅ AI model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load AI model: {e}")
    schedule_parser = None
    model_nlp = None

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
    
    for day in day_names:
        normalized = normalized.replace(day.lower(), day.title())
        normalized = normalized.replace(day.upper(), day.title())
    
    return normalized

@app.route("/api/parse", methods=["POST"])
def parse_input():
    if not schedule_parser:
        return jsonify({"error": "AI model not available"}), 500
        
    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "Missing text input"}), 400

    text = data["text"].strip()
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
                "day": ent.text.strip().capitalize()[:3]
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
    generation_start_time = time.time()

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
    parsed_constraints = {"constraints": constraints} if isinstance(constraints, list) else parse_course_text(constraints)

    try:
        courses = []
        for i, c in enumerate(data["courses"]):
            if not isinstance(c, dict):
                return jsonify({"error": f"Invalid course format at index {i}"}), 400
            
            if not c.get("name"):
                return jsonify({"error": f"Missing name for course at index {i}"}), 400
            if not c.get("lectures"):
                return jsonify({"error": f"Missing lectures for {c['name']}"}), 400
            if not c.get("ta_times"):
                return jsonify({"error": f"Missing TA times for {c['name']}"}), 400

            lectures = [str(l) for l in c["lectures"]] if isinstance(c["lectures"], list) else c["lectures"].split(",")
            ta_times = [str(t) for t in c["ta_times"]] if isinstance(c["ta_times"], list) else c["ta_times"].split(",")

            lec_slots = [parse_time_slot(s.strip()) for s in lectures if s]
            ta_slots = [parse_time_slot(s.strip()) for s in ta_times if s]

            if not any(lec_slots):
                return jsonify({"error": f"Invalid lecture time format for {c['name']}"}), 400
            if not any(ta_slots):
                return jsonify({"error": f"Invalid TA time format for {c['name']}"}), 400

            courses.append({
                "name": c["name"],
                "lectures": [s for s in lec_slots if s],
                "ta_times": [s for s in ta_slots if s]
            })

        schedule = generate_schedule(
            courses=courses,
            preference=preference,
            constraints=parsed_constraints.get("constraints") if parsed_constraints else None
        )

        generation_time_ms = int((time.time() - generation_start_time) * 1000)
        
        # Log generation attempt if user is authenticated
        user_id = session.get('user_id')
        if user_id:
            try:
                from auth.auth_manager import AuthManager
                
                auth_manager = AuthManager()
                client = auth_manager.get_client_for_user(user_id)
                
                log_data = {
                    'user_id': user_id,
                    'courses_count': len(courses),
                    'constraints_count': len(parsed_constraints.get("constraints", [])) if parsed_constraints else 0,
                    'generation_time_ms': generation_time_ms,
                    'schedule_type': preference,
                    'success': schedule is not None,
                    'error_message': None if schedule else 'No valid schedule found'
                }
                
                client.table("schedule_generation_logs").insert(log_data).execute()
                
            except Exception as stats_error:
                print(f"Error logging statistics: {stats_error}")

        if schedule is None:
            return jsonify({
                "error": "No valid schedule found",
                "details": "Could not find a schedule that satisfies all constraints"
            }), 200

        return jsonify({"schedule": schedule}), 200

    except Exception as e:
        print(f"Error generating schedule: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Add a test endpoint to check session status
@app.route("/api/test-session", methods=["GET"])
def test_session():
    """Test endpoint to check session status"""
    return jsonify({
        "session_data": dict(session),
        "user_id": session.get('user_id'),
        "authenticated": session.get('authenticated', False),
        "cookies": dict(request.cookies),
        "headers": dict(request.headers),
        "session_permanent": session.permanent,
        "session_new": session.new if hasattr(session, 'new') else 'unknown'
    }), 200

if __name__ == "__main__":
    # Use 127.0.0.1 consistently
    app.run(debug=True, host='127.0.0.1', port=5000)