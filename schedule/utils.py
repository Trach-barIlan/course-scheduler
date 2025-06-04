import re

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def parse_time_slot(s):
    match = re.match(r'([A-Za-z]+)\s+(\d+)-(\d+)', s.strip())
    if match:
        day, start, end = match.groups()
        return (day, int(start), int(end))
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
