from itertools import product
from .utils import time_conflict, count_days_used, count_hour_gaps

def generate_schedule(courses, preference="crammed", constraints=None):
    all_combos = [product(c["lectures"], c["ta_times"]) for c in courses]
    possible_schedules = product(*all_combos)
    valid_schedules = []

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

        # Check constraints if provided
        if valid and constraints:
            for constraint in constraints:
                constraint_type = constraint.get("type", "")
                print(f"Checking constraint: {constraint_type}")
                
                if constraint_type == "No Class Day":
                    forbidden_day = constraint.get("day")
                    print(f"Checking for forbidden day: {forbidden_day}")
                    for slot in time_slots:
                        print(f"Checking slots: {slot}")
                    if any(slot[0] == forbidden_day for slot in time_slots):
                        valid = False
                        break
                
                elif constraint_type == "No Class Before":
                    earliest_allowed = constraint.get("time", 9)
                    if any(slot[1] < earliest_allowed for slot in time_slots):
                        valid = False
                        break
                
                elif constraint_type == "No Class After":
                    latest_allowed = constraint.get("time", 17)
                    if any(slot[2] > latest_allowed for slot in time_slots):
                        valid = False
                        break
                
                elif constraint_type == "Avoid Ta":
                    ta_name = constraint.get("name", "").strip()
                    # Extract course and TA information from schedule
                    for i, (_, ta_slot) in enumerate(schedule):
                        course_info = courses[i]
                        # Check if this TA slot belongs to the TA to avoid
                        if ta_name.lower() in str(ta_slot).lower():
                            valid = False
                            break

        if valid:
            valid_schedules.append((schedule, time_slots))

    if not valid_schedules:
        return None

    if preference == "crammed":
        ranked = sorted(valid_schedules, key=lambda s: (count_days_used(s[1]), count_hour_gaps(s[1])))
    elif preference == "spaced":
        ranked = sorted(valid_schedules, key=lambda s: (-count_days_used(s[1]), -count_hour_gaps(s[1])))
    else:
        ranked = valid_schedules

    best_schedule = ranked[0][0]
    return [
        {
            "name": courses[i]["name"],
            "lecture": f"{best_schedule[i][0][0]} {best_schedule[i][0][1]}-{best_schedule[i][0][2]}",
            "ta": f"{best_schedule[i][1][0]} {best_schedule[i][1][1]}-{best_schedule[i][1][2]}"
        }
        for i in range(len(courses))
    ]
