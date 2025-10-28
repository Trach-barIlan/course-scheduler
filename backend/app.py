from flask import Flask, request, jsonify, g
from flask_cors import CORS
from schedule.logic import generate_schedule
from schedule.utils import parse_time_slot
from schedule.parserAI import parse_course_text
from ai_model.ml_parser import ScheduleParser
from auth.routes import auth_bp, token_required
from api.schedules import schedules_bp
from api.statistics import statistics_bp
from api.university import university_bp
from api.contact import contact_bp

from api.supabase_courses import supabase_courses_bp  # Database-based API for course details
from api.hybrid_autocomplete import hybrid_autocomplete_bp  # Fast JSON-based autocomplete
# from api.courses import courses_bp  # Old JSON-based API (commented out)
from auth.auth_manager import AuthManager
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
import time
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Simplified configuration - no session management needed
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
origins = [origin.strip() for origin in origins] # Remove whitespace
print(f"Configured CORS origins: {origins}")

# Enhanced CORS configuration
CORS(app, 
     origins=origins,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Register blueprints with /api/ prefix restored
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(schedules_bp, url_prefix='/api/schedules')
app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
app.register_blueprint(university_bp, url_prefix='/api/university')
app.register_blueprint(contact_bp, url_prefix='/api')
app.register_blueprint(supabase_courses_bp, url_prefix='/api')  # Database-based API for course details
app.register_blueprint(hybrid_autocomplete_bp, url_prefix='/api')  # Fast JSON-based autocomplete
# app.register_blueprint(courses_bp, url_prefix='/api')  # Old JSON-based API
print("✅ University API registered successfully")
print("✅ Supabase courses API registered successfully")
print("✅ Hybrid autocomplete API registered successfully")

# Initialize AI parser with timeout handling
schedule_parser = None
model_nlp = None

def initialize_ai_model():
    """Initialize AI model in a separate thread to avoid blocking startup"""
    global schedule_parser, model_nlp
    print(f"🔍 AI Model Init - Starting initialization...")
    print(f"🔍 AI Model Init - SKIP_AI_MODEL env var: {os.environ.get('SKIP_AI_MODEL')}")
    print(f"🔍 AI Model Init - Working directory: {os.getcwd()}")
    print(f"🔍 AI Model Init - Python path: {os.sys.path}")
    
    if not os.environ.get('SKIP_AI_MODEL'):
        try:
            print("🔄 Loading AI model...")
            print("🔍 AI Model Init - About to import ScheduleParser...")
            
            # Check if ai_model directory exists
            ai_model_path = os.path.join(os.getcwd(), 'ai_model')
            print(f"🔍 AI Model Init - AI model directory path: {ai_model_path}")
            print(f"🔍 AI Model Init - AI model directory exists: {os.path.exists(ai_model_path)}")
            
            if os.path.exists(ai_model_path):
                print(f"🔍 AI Model Init - AI model directory contents: {os.listdir(ai_model_path)}")
                schedule_ner_path = os.path.join(ai_model_path, 'schedule_ner')
                print(f"🔍 AI Model Init - Schedule NER path: {schedule_ner_path}")
                print(f"🔍 AI Model Init - Schedule NER exists: {os.path.exists(schedule_ner_path)}")
                if os.path.exists(schedule_ner_path):
                    print(f"🔍 AI Model Init - Schedule NER contents: {os.listdir(schedule_ner_path)}")
            
            from ai_model.ml_parser import ScheduleParser
            print("✅ AI Model Init - ScheduleParser imported successfully")
            
            schedule_parser = ScheduleParser()
            print(f"🔍 AI Model Init - ScheduleParser instantiated successfully: {schedule_parser is not None}")

            
            model_nlp = schedule_parser.nlp
            print(f"🔍 AI Model Init - NLP model loaded: {model_nlp is not None}")
            
            print("✅ AI model loaded successfully")
        except ImportError as e:
            print(f"❌ AI Model Init - Import error: {e}")
            print(f"❌ AI Model Init - Import error type: {type(e)}")
            import traceback
            print(f"❌ AI Model Init - Import traceback: {traceback.format_exc()}")
            schedule_parser = None
            model_nlp = None
        except Exception as e:
            print(f"❌ Failed to load AI model: {e}")
            print(f"❌ AI Model Init - Error type: {type(e)}")
            import traceback
            print(f"❌ AI Model Init - Full traceback: {traceback.format_exc()}")
            schedule_parser = None
            model_nlp = None
    else:
        print("⏭️ Skipping AI model initialization (SKIP_AI_MODEL is set)")
        schedule_parser = None
        model_nlp = None
    
    print(f"🔍 AI Model Init - Final state: schedule_parser={schedule_parser is not None}, model_nlp={model_nlp is not None}")

# Initialize AI model in background
import threading
print("🔍 Starting AI model initialization thread...")
ai_thread = threading.Thread(target=initialize_ai_model)
ai_thread.daemon = True
ai_thread.start()
print("🔍 AI model initialization thread started")

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

def update_user_statistics_after_generation(user_id, courses_count, constraints_count, generation_time_ms, schedule_type, success):
    """Update user statistics after schedule generation"""
    try:
        auth_manager = AuthManager()
        client = auth_manager.get_client_for_user(user_id)
        
        # Call the database function to update statistics
        client.rpc('update_user_statistics', {
            'p_user_id': user_id,
            'p_courses_count': courses_count,
            'p_constraints_count': constraints_count,
            'p_generation_time_ms': generation_time_ms,
            'p_schedule_type': schedule_type,
            'p_success': success
        }).execute()
        
        print(f"✅ Updated statistics for user {user_id}")
        
    except Exception as e:
        print(f"⚠️ Failed to update user statistics: {e}")

@app.route("/api/parse", methods=["POST"])
@token_required
def parse_input():
    print("🔍 CONSTRAINT PARSING: Starting parse_input endpoint")
    print(f"🔍 CONSTRAINT PARSING: schedule_parser available: {schedule_parser is not None}")
    print(f"🔍 CONSTRAINT PARSING: model_nlp available: {model_nlp is not None}")
    
    if not schedule_parser or not model_nlp:
        print("❌ CONSTRAINT PARSING: AI model not available - returning error")
        return jsonify({"error": "AI model not available"}), 500
        
    data = request.json
    print(f"🔍 CONSTRAINT PARSING: Received data: {data}")
    
    if not data or "text" not in data:
        print("❌ CONSTRAINT PARSING: Missing text input")
        return jsonify({"error": "Missing text input"}), 400

    text = data["text"].strip()
    print(f"🔍 CONSTRAINT PARSING: Original text: '{text}'")
    
    normalized_text = normalize_text(text)
    print(f"🔍 CONSTRAINT PARSING: Normalized text: '{normalized_text}'")
    
    print("🔍 CONSTRAINT PARSING: About to process with NLP model")
    try:
        doc = model_nlp(normalized_text)
        print(f"🔍 CONSTRAINT PARSING: NLP processing successful, found {len(doc.ents)} entities")
    except Exception as e:
        print(f"❌ CONSTRAINT PARSING: NLP processing failed: {e}")
        import traceback
        print(f"❌ CONSTRAINT PARSING: Full traceback: {traceback.format_exc()}")
        return jsonify({"error": f"NLP processing failed: {str(e)}"}), 500

    constraints = []
    raw_entities = []

    print("🔍 CONSTRAINT PARSING: Starting entity processing...")
    for i, ent in enumerate(doc.ents):
        print(f"🔍 CONSTRAINT PARSING: Processing entity {i+1}: '{ent.text}' (label: {ent.label_})")
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
            ta_name = ent.text.replace("ta", "").replace("TA", "").strip()
            if ta_name:
                constraints.append({
                    "type": "Avoid TA",
                    "name": ta_name
                })
            

    return jsonify({
        "constraints": constraints,
        "entities": raw_entities
    }, 200)

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
    print(f"🔍 SCHEDULE PARSING: Received constraints: {constraints}")
    print(f"🔍 SCHEDULE PARSING: Constraints type: {type(constraints)}")
    print(f"🔍 SCHEDULE PARSING: Is constraints a list? {isinstance(constraints, list)}")
    
    if isinstance(constraints, list):
        print("🔍 SCHEDULE PARSING: Constraints already in list format, skipping parsing")
        parsed_constraints = {"constraints": constraints}
    else:
        print("🔍 SCHEDULE PARSING: Need to parse constraints text...")
        print(f"🔍 SCHEDULE PARSING: About to call parse_course_text with: '{constraints}'")
        try:
            parsed_constraints = parse_course_text(constraints)
            print(f"🔍 SCHEDULE PARSING: parse_course_text succeeded: {parsed_constraints}")
        except Exception as e:
            print(f"❌ SCHEDULE PARSING: parse_course_text failed: {e}")
            import traceback
            print(f"❌ SCHEDULE PARSING: Full traceback: {traceback.format_exc()}")
            return jsonify({"error": f"Constraint parsing failed: {str(e)}"}), 500

    try:
        courses = []
        for i, c in enumerate(data["courses"]):
            if not isinstance(c, dict):
                return jsonify({"error": f"Invalid course format at index {i}"}), 400
            
            if not c.get("name"):
                return jsonify({"error": f"Missing name for course at index {i}"}), 400

            lectures = [str(l) for l in c["lectures"]] if isinstance(c["lectures"], list) else c["lectures"].split(",")
            ta_times = [str(t) for t in c["ta_times"]] if isinstance(c["ta_times"], list) else c["ta_times"].split(",")

            lec_slots = [parse_time_slot(s.strip()) for s in lectures if s]
            ta_slots = [parse_time_slot(s.strip()) for s in ta_times if s]


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
        
        # Log generation attempt and update statistics if user is authenticated
        user = getattr(g, 'user', None)
        success = schedule is not None
        
        if user:
            try:
                auth_manager = AuthManager()
                client = auth_manager.get_client_for_user(user['id'])
                
                # Log the generation attempt
                log_data = {
                    'user_id': user['id'],
                    'courses_count': len(courses),
                    'constraints_count': len(parsed_constraints.get("constraints", [])) if parsed_constraints else 0,
                    'generation_time_ms': generation_time_ms,
                    'schedule_type': preference,
                    'success': success,
                    'error_message': None if success else 'No valid schedule found'
                }
                
                client.table("schedule_generation_logs").insert(log_data).execute()
                
                # Update user statistics
                update_user_statistics_after_generation(
                    user['id'],
                    len(courses),
                    len(parsed_constraints.get("constraints", [])) if parsed_constraints else 0,
                    generation_time_ms,
                    preference,
                    success
                )
                
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

# Add a test endpoint to check authentication
@app.route("/api/test-session", methods=["GET"])
@token_required
def test_session():
    """Test endpoint to check authentication status"""
    try:
        user = g.user
        
        return jsonify({
            "user": user,
            "authenticated": True,
            "auth_header": request.headers.get('Authorization', 'Not provided'),
            "status": "success"
        }), 200
        
    except Exception as e:
        print(f"❌ Error in test_session: {e}")
        traceback.print_exc()
        
        return jsonify({
            "error": "Authentication check failed",
            "details": str(e),
            "user": None,
            "authenticated": False,
            "auth_header": request.headers.get('Authorization', 'Not provided'),
            "status": "error"
        }), 500

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "ai_model_loaded": schedule_parser is not None,
        "time": time.time()
    }), 200


# if __name__ == "__main__":
#     # אפשר לדלג על מודל (לבדיקה ראשונית):
#     # set SKIP_AI_MODEL=1  (ב-PowerShell: $env:SKIP_AI_MODEL="1")
#     port = int(os.environ.get("PORT", 5001))
#     host = os.environ.get("HOST", "0.0.0.0")
#     debug = os.environ.get("FLASK_DEBUG", "1") == "1"

#     print(f"🚀 Starting Flask server on http://{host}:{port} (debug={debug})")
#     # אם אתה מעדיף להמתין לטעינת המודל לפני עלייה:
#     # if not os.environ.get("SKIP_AI_MODEL"): initialize_ai_model()

#     app.run(host=host, port=port, debug=debug, use_reloader=debug)