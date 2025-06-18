from flask import Flask, request, jsonify, session
from flask_cors import CORS
from schedule.logic import generate_schedule  # Remove parse_time_slot from here
from schedule.utils import parse_time_slot
from schedule.parserAI import parse_course_text
from ai_model.ml_parser import ScheduleParser
from auth.routes_supabase import auth_bp  # Updated import
from api.schedules import schedules_bp  # Add schedules API
from api.statistics import statistics_bp  # Add statistics API
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced session configuration for better persistence
#app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')
app.secret_key = "your-secret-key-change-this-in-production"  # Replace with your actual secret key
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'schedgic_session'
app.config['SESSION_COOKIE_PATH'] = '/'

# Enhanced CORS configuration with credentials support
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Set-Cookie"],
        "max_age": 86400  # Cache preflight requests for 24 hours
    }
}, supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(schedules_bp, url_prefix='/api/schedules')
app.register_blueprint(statistics_bp, url_prefix='/api/statistics')

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

@app.before_request
def before_request():
    """Enhanced session management and authentication check"""
    session.permanent = True
    
    # Enhanced debug logging for session state
    if request.endpoint and 'api' in request.endpoint:
        print(f"\n🔍 === REQUEST DEBUG INFO ===")
        print(f"Endpoint: {request.endpoint}")
        print(f"Method: {request.method}")
        print(f"Session ID: {session.get('user_id', 'No session ID')}")
        print(f"Session permanent: {session.permanent}")
        print(f"Session data: {dict(session)}")
        print(f"Request cookies: {dict(request.cookies)}")
        print(f"User authenticated: {session.get('authenticated', False)}")
        print(f"User ID: {session.get('user_id', 'None')}")
        print(f"=== END DEBUG INFO ===\n")

    # Auto-refresh session for authenticated endpoints (except auth endpoints)
    if (request.endpoint and 
        'api' in request.endpoint and 
        'auth' not in request.endpoint and 
        request.method != 'OPTIONS'):
        
        user_id = session.get('user_id')
        authenticated = session.get('authenticated', False)
        
        # If we have a user_id but not authenticated flag, try to restore session
        if user_id and not authenticated:
            print(f"🔄 Attempting to restore session for user: {user_id}")
            try:
                from auth.supabase_client import SupabaseClient
                supabase = SupabaseClient()
                
                # Try to get user profile to verify they still exist
                profile = supabase.supabase.table("user_profiles").select("*").eq("id", user_id).execute()
                
                if profile.data:
                    user_data = profile.data[0]
                    # Restore full session
                    session['user_id'] = user_data['id']
                    session['username'] = user_data.get('username', '')
                    session['email'] = user_data.get('email', '')
                    session['first_name'] = user_data.get('first_name', '')
                    session['last_name'] = user_data.get('last_name', '')
                    session['authenticated'] = True
                    session.permanent = True
                    print(f"✅ Session restored for user: {user_data.get('username')}")
                else:
                    print(f"❌ User {user_id} no longer exists, clearing session")
                    session.clear()
                    
            except Exception as e:
                print(f"❌ Error restoring session: {e}")

@app.after_request
def after_request(response):
    """Enhanced response handling with session persistence"""
    if request.endpoint and 'api' in request.endpoint:
        print(f"\n📤 === RESPONSE DEBUG INFO ===")
        print(f"Status: {response.status_code}")
        print(f"Session after request: {dict(session)}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"=== END RESPONSE INFO ===\n")
    
    # Ensure session cookies are properly set
    if session.get('user_id'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

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
    
    # Track generation start time
    generation_start_time = time.time()

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

        # Calculate generation time
        generation_time_ms = int((time.time() - generation_start_time) * 1000)
        
        # Log the generation attempt (if user is authenticated)
        user_id = session.get('user_id')
        if user_id:
            try:
                # Import here to avoid circular imports
                from api.statistics import statistics_bp
                from auth.supabase_client import SupabaseClient
                
                supabase = SupabaseClient()
                
                # Log generation
                log_data = {
                    'user_id': user_id,
                    'courses_count': len(courses),
                    'constraints_count': len(parsed_constraints.get("constraints", [])) if parsed_constraints else 0,
                    'generation_time_ms': generation_time_ms,
                    'schedule_type': preference,
                    'success': schedule is not None,
                    'error_message': None if schedule else 'No valid schedule found'
                }
                
                supabase.supabase.table("schedule_generation_logs").insert(log_data).execute()
                
                # Update user statistics if successful
                if schedule:
                    supabase.supabase.rpc('update_user_statistics', {
                        'p_user_id': user_id,
                        'p_courses_count': len(courses),
                        'p_constraints_count': len(parsed_constraints.get("constraints", [])) if parsed_constraints else 0,
                        'p_generation_time_ms': generation_time_ms,
                        'p_schedule_type': preference,
                        'p_success': True
                    }).execute()
                    
            except Exception as stats_error:
                print(f"Error logging statistics: {stats_error}")
                # Don't fail the request if statistics logging fails

        if schedule is None:
            return jsonify({
                "error": "No valid schedule found",
                "details": "Could not find a schedule that satisfies all constraints"
            }), 200

        return jsonify({"schedule": schedule}), 200

    except Exception as e:
        app.logger.error(f"Error generating schedule: {str(e)}")
        
        # Log failed generation attempt
        user_id = session.get('user_id')
        if user_id:
            try:
                from auth.supabase_client import SupabaseClient
                supabase = SupabaseClient()
                
                generation_time_ms = int((time.time() - generation_start_time) * 1000)
                log_data = {
                    'user_id': user_id,
                    'courses_count': len(data.get("courses", [])),
                    'constraints_count': len(parsed_constraints.get("constraints", [])) if parsed_constraints else 0,
                    'generation_time_ms': generation_time_ms,
                    'schedule_type': preference,
                    'success': False,
                    'error_message': str(e)
                }
                
                supabase.supabase.table("schedule_generation_logs").insert(log_data).execute()
                
            except Exception as stats_error:
                print(f"Error logging failed generation: {stats_error}")
        
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)