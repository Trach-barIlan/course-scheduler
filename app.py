from flask import Flask, request, jsonify
from flask_cors import CORS
from schedule.logic import generate_schedule  # Remove parse_time_slot from here
from schedule.utils import parse_time_slot
from schedule.parserAI import parse_course_text

app = Flask(__name__)
CORS(app)

@app.route("/api/parse", methods=["POST"])
def parse_input():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "text" not in data:
        return jsonify({"error": "Missing text input"}), 400
    if not data["text"].strip():
        return jsonify({"error": "Empty text input"}), 400

    try:
        parsed_data = parse_course_text(data["text"])
        if not parsed_data:
            return jsonify({"error": "Failed to parse input"}), 400
        return jsonify(parsed_data), 200
    except Exception as e:
        app.logger.error(f"Error parsing text: {str(e)}")
        return jsonify({"error": "Failed to parse text input"}), 500

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
