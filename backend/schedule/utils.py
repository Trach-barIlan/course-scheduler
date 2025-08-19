import re

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

def parse_time_slot(s):
    match = re.match(r'([A-Za-z]+)\s+(\d+)-(\d+)', s.strip())
    if match:
        day, start, end = match.groups()
        # Add day standardization
        day_map = {
            # Standardize day names
            "monday": "Mon",
            "tuesday": "Tue",
            "wednesday": "Wed",
            "thursday": "Thu",
            "friday": "Fri",
            "saturday": "Sat",
            "sunday": "Sun",
            # Capitalize full names
            "Monday": "Mon",
            "Tuesday": "Tue",
            "Wednesday": "Wed",
            "Thursday": "Thu",
            "Friday": "Fri",
            "Saturday": "Sat",
            "Sunday": "Sun",
            # Add abbreviated versions
            "mon": "Mon",
            "tue": "Tue",
            "wed": "Wed",
            "thu": "Thu",
            "fri": "Fri",
            "sat": "Sat",
            "sun": "Sun"
        }
        
        standardized_day = day_map.get(day.lower())
        if standardized_day is None:
            print(f"Warning: Invalid day format '{day}', must be one of {list(day_map.keys())}")
            return None
            
        return (standardized_day, int(start), int(end))
    return None

def time_conflict(slot1, slot2):
    return slot1[0] == slot2[0] and not (slot1[2] <= slot2[1] or slot2[2] <= slot1[1])

def count_days_used(time_slots):
    return len(set(slot[0] for slot in time_slots))

def count_hour_gaps(time_slots):
    sorted_slots = sorted(time_slots, key=lambda x: (DAYS.index(x[0]), x[1]))
    gaps = 0
    prev_day = None
    prev_end = 0
    for day, start, end in sorted_slots:
        if day == prev_day and start > prev_end:
            gaps += start - prev_end
        prev_day = day
        prev_end = end
    return gaps
