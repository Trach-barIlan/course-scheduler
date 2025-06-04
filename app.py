from flask import Flask, request, jsonify
from itertools import product
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def parse_time_slot(s):
    match = re.match(r'([A-Za-z]+)\s+(\d+)-(\d+)', s.strip())
    if match:
        day, start, end = match.groups()
        return (day, int(start), int(end))
    return None

def time_conflict(slot1, slot2):
    return slot1[0] == slot2[0] and not (slot1[2] <= slot2[1] or slot2[2] <= slot1[1])

def generate_schedule(courses):
    all_combos = [product(c["lectures"], c["ta_times"]) for c in courses]
    possible_schedules = product(*all_combos)

    for schedule in possible_schedules:
        time_slots = []
        valid = True

        for (lecture, ta) in schedule:
            if time_conflict(lecture, ta):
                valid = False
                break

            for existing in time_slots:
                if time_conflict(lecture, existing) or time_conflict(ta, existing):
                    valid = False
                    break

            if not valid:
                break

            time_slots.extend([lecture, ta])

        if valid:
            return [
                {
                    "name": courses[i]["name"],
                    "lecture": f"{schedule[i][0][0]} {schedule[i][0][1]}-{schedule[i][0][2]}",
                    "ta": f"{schedule[i][1][0]} {schedule[i][1][1]}-{schedule[i][1][2]}"
                }
                for i in range(len(courses))
            ]

    return None

@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    data = request.json
    if not data or "courses" not in data:
        return jsonify({"error": "Invalid input, expected JSON with 'courses'"}), 400

    courses_input = data["courses"]
    courses = []
    for c in courses_input:
        lec_slots = [parse_time_slot(s) for s in c.get("lectures", []) if parse_time_slot(s)]
        ta_slots = [parse_time_slot(s) for s in c.get("ta_times", []) if parse_time_slot(s)]
        courses.append({"name": c.get("name", "Unnamed"), "lectures": lec_slots, "ta_times": ta_slots})

    schedule = generate_schedule(courses)
    if schedule is None:
        return jsonify({"error": "No valid schedule found"}), 200
    return jsonify({"schedule": schedule}), 200


if __name__ == "__main__":
    app.run(debug=True)
