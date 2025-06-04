from flask import Flask, request, jsonify
from flask_cors import CORS
from schedule.logic import generate_schedule  # Remove parse_time_slot from here
from schedule.utils import parse_time_slot

app = Flask(__name__)
CORS(app)

@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    data = request.json
    if not data or "courses" not in data:
        return jsonify({"error": "Invalid input, expected JSON with 'courses'"}), 400

    preference = data.get("preference", "crammed")
    courses_input = data["courses"]
    courses = []
    for c in courses_input:
        lec_slots = [parse_time_slot(s) for s in c.get("lectures", []) if parse_time_slot(s)]
        ta_slots = [parse_time_slot(s) for s in c.get("ta_times", []) if parse_time_slot(s)]
        courses.append({"name": c.get("name", "Unnamed"), "lectures": lec_slots, "ta_times": ta_slots})

    schedule = generate_schedule(courses, preference)
    if schedule is None:
        return jsonify({"error": "No valid schedule found"}), 200
    return jsonify({"schedule": schedule}), 200

if __name__ == "__main__":
    app.run(debug=True)
