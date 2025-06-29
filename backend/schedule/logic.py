from itertools import product
from .utils import time_conflict, count_days_used, count_hour_gaps

def generate_schedule(courses, preference="crammed", constraints=None):
    # If lectures or ta_times is empty, use [None] as a placeholder
    all_combos = [
        product(
            c["lectures"] if c["lectures"] else [None],
            c["ta_times"] if c["ta_times"] else [None]
        )
        for c in courses
    ]
    possible_schedules = product(*all_combos)
    valid_schedules = []

    for schedule in possible_schedules:
        time_slots = []
        valid = True

        for (lecture, ta) in schedule:
            # Skip None slots for conflict checking
            if lecture is not None and ta is not None and time_conflict(lecture, ta):
                valid = False
                break
            for existing in time_slots:
                if lecture is not None and time_conflict(lecture, existing):
                    valid = False
                    break
                if ta is not None and time_conflict(ta, existing):
                    valid = False
                    break
            if not valid:
                break
            # Only add non-None slots
            if lecture is not None:
                time_slots.append(lecture)
            if ta is not None:
                time_slots.append(ta)

        # Check constraints if provided
        if valid and constraints:
            for constraint in constraints:
                constraint_type = constraint.get("type", "")
                if constraint_type == "No Class Day":
                    forbidden_day = constraint.get("day")
                    if any(slot is not None and slot[0] == forbidden_day for slot in time_slots):
                        valid = False
                        break
                elif constraint_type == "No Class Before":
                    earliest_allowed = constraint.get("time", 9)
                    if any(slot is not None and slot[1] < earliest_allowed for slot in time_slots):
                        valid = False
                        break
                elif constraint_type == "No Class After":
                    latest_allowed = constraint.get("time", 17)
                    if any(slot is not None and slot[2] > latest_allowed for slot in time_slots):
                        valid = False
                        break
                elif constraint_type == "Avoid Ta":
                    ta_name = constraint.get("name", "").strip()
                    for i, (_, ta_slot) in enumerate(schedule):
                        if ta_slot is not None and ta_name.lower() in str(ta_slot).lower():
                            valid = False
                            break

        if valid:
            valid_schedules.append((schedule, time_slots))

    if not valid_schedules:
        return None

    if preference == "crammed":
        ranked = sorted(valid_schedules, key=lambda s: (count_days_used([slot for slot in s[1] if slot is not None]), count_hour_gaps([slot for slot in s[1] if slot is not None])))
    elif preference == "spaced":
        ranked = sorted(valid_schedules, key=lambda s: (-count_days_used([slot for slot in s[1] if slot is not None]), -count_hour_gaps([slot for slot in s[1] if slot is not None])))
    else:
        ranked = valid_schedules

    best_schedule = ranked[0][0]
    return [
        {
            "name": courses[i]["name"],
            "lecture": f"{best_schedule[i][0][0]} {best_schedule[i][0][1]}-{best_schedule[i][0][2]}" if best_schedule[i][0] is not None else None,
            "ta": f"{best_schedule[i][1][0]} {best_schedule[i][1][1]}-{best_schedule[i][1][2]}" if best_schedule[i][1] is not None else None
        }
        for i in range(len(courses))
    ]