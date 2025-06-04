from flask import Flask, request, render_template
from itertools import product
import re

app = Flask(__name__)

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

# Converts "Mon 9-11" → ("Mon", 9, 11)
def parse_time_slot(s):
    match = re.match(r'([A-Za-z]+)\s+(\d+)-(\d+)', s.strip())
    if match:
        day, start, end = match.groups()
        return (day, int(start), int(end))
    return None

# Checks for time overlap between two time slots
def time_conflict(slot1, slot2):
    return slot1[0] == slot2[0] and not (slot1[2] <= slot2[1] or slot2[2] <= slot1[1])

def generate_schedule(courses):
    all_combos = [product(c["lectures"], c["ta_times"]) for c in courses]
    possible_schedules = product(*all_combos)

    for schedule in possible_schedules:
        time_slots = []
        valid = True

        for (lecture, ta) in schedule:
            # ✅ Step 1: Check lecture vs TA (same course)
            if time_conflict(lecture, ta):
                valid = False
                break

            # ✅ Step 2: Check against other already-added slots
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        course_names = request.form.getlist("course_name")
        lectures = request.form.getlist("lectures")
        ta_times = request.form.getlist("ta_times")

        courses = []
        for name, lec_str, ta_str in zip(course_names, lectures, ta_times):
            lec_slots = [parse_time_slot(s) for s in lec_str.split(",")]
            ta_slots = [parse_time_slot(s) for s in ta_str.split(",")]
            courses.append({"name": name, "lectures": lec_slots, "ta_times": ta_slots})

        schedule = generate_schedule(courses)
        return render_template("schedule.html", schedule=schedule)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
