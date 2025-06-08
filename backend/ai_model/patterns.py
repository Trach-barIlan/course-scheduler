PATTERNS = [
        # Basic time patterns
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [{"LIKE_NUM": True}, {"LOWER": {"IN": ["am", "pm"]}}]
        },
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [{"LIKE_NUM": True}, {"TEXT": ":"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["am", "pm"]}}]
        },
        # Handle times without am/pm
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [{"LIKE_NUM": True}, {"TEXT": ":"}, {"LIKE_NUM": True}]
        },
        # Handle written numbers
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [{"LOWER": {"IN": ["ten", "eleven", "nine", "eight"]}}, {"LOWER": {"IN": ["am", "pm"]}}]
        },
        # Handle o'clock format
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [{"LIKE_NUM": True}, {"LOWER": "o'clock"}]
        },
        # Handle military time
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [{"TEXT": {"REGEX": "^([0-1]?[0-9]|2[0-3])[0-5][0-9]$"}}]
        },
        {
            "label": "NO_CLASS_DAY",
            "pattern": [{"LOWER": {"IN": ["monday", "tuesday", "wednesday", "thursday", "friday"]}}]
        },
        {
            "label": "NO_CLASS_DAY",
            "pattern": [{"TEXT": {"REGEX": "(?i)^(monday|tuesday|wednesday|thursday|friday)$"}}]
        },
        {
            "label": "AVOID_TA",
            "pattern": [{"LOWER": "ta"}, {"IS_TITLE": True}]
        }
    ]