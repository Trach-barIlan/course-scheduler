PATTERNS = [
        # NO_CLASS_BEFORE patterns with explicit before indicators
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [
                {"LOWER": {"IN": ["before", "until", "till", "earlier"]}},
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["am", "pm"]}}
            ]
        },
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [
                {"LOWER": {"IN": ["before", "until", "till", "earlier"]}},
                {"LIKE_NUM": True},
                {"TEXT": ":"},
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["am", "pm"]}}
            ]
        },
        {
            "label": "NO_CLASS_BEFORE",
            "pattern": [
                {"LOWER": "no"},
                {"LOWER": "earlier"},
                {"LOWER": "than"},
                {"LIKE_NUM": True}
            ]
        },
        
        # NO_CLASS_AFTER patterns with explicit after indicators
        {
            "label": "NO_CLASS_AFTER",
            "pattern": [
                {"LOWER": {"IN": ["after", "past", "beyond", "later"]}},
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["pm", "am"]}}
            ]
        },
        {
            "label": "NO_CLASS_AFTER",
            "pattern": [
                {"LOWER": {"IN": ["after", "past", "beyond", "later"]}},
                {"LIKE_NUM": True},
                {"TEXT": ":"},
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["pm", "am"]}}
            ]
        },
        {
            "label": "NO_CLASS_AFTER",
            "pattern": [
                {"LOWER": {"IN": ["finish", "end", "done"]}},
                {"LOWER": "by"},
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["pm", "am"]}}
            ]
        },
        
        # NO_CLASS_DAY patterns
        {
            "label": "NO_CLASS_DAY",
            "pattern": [{"LOWER": {"IN": ["monday", "tuesday", "wednesday", "thursday", "friday"]}}]
        },
        {
            "label": "NO_CLASS_DAY",
            "pattern": [
                {"LOWER": "no"},
                {"LOWER": {"IN": ["monday", "tuesday", "wednesday", "thursday", "friday"]}},
                {"LOWER": {"IN": ["class", "classes"]}}
            ]
        },
        
        # AVOID_TA patterns
        {
            "label": "AVOID_TA",
            "pattern": [{"LOWER": "ta"}, {"IS_TITLE": True}]
        },
        {
            "label": "AVOID_TA",
            "pattern": [
                {"LOWER": {"IN": ["avoid", "no"]}},
                {"LOWER": "ta"},
                {"IS_TITLE": True}
            ]
        }
]