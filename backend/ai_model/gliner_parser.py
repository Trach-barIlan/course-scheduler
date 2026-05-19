from gliner import GLiNER
import re
from typing import Dict, List, Any

class GlinerParser:
    """
    Zero-shot NER parser using GLiNER for flexible constraint extraction.
    Combines GLiNER for robust extraction with improved classification logic.
    """
    def __init__(self, model_name: str = "urchade/gliner_small-v2.1"):
        print(f"🔍 GLINER PARSER: Initializing with model {model_name}...")
        try:
            self.model = GLiNER.from_pretrained(model_name)
            # Focused labels for better extraction
            self.labels = ["time", "day", "person name"]
            print("✅ GLINER PARSER: Model loaded successfully")
        except Exception as e:
            print(f"❌ GLINER PARSER: Failed to load model: {e}")
            raise

    def extract_hour(self, text: str) -> int:
        """Converts time expressions (e.g., '10am', '15:30', 'noon') to 24-hour integer hours."""
        text = text.lower().strip()
        
        if "noon" in text:
            return 12
        if "midnight" in text:
            return 0

        # Regex for HH:MM or HH (am/pm)
        match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text)
        if not match:
            return None

        hour = int(match.group(1))
        # Check for am/pm in the extracted text or surrounding
        if "pm" in text and hour < 12:
            hour += 12
        elif "am" in text and hour == 12:
            hour = 0
            
        return hour

    def parse(self, text: str, threshold: float = 0.3) -> Dict[str, Any]:
        """Parse text to extract scheduling constraints."""
        print(f"🔍 GLINER PARSER: Parsing text: '{text}' (threshold={threshold})")
        
        entities = self.model.predict_entities(text, self.labels, threshold=threshold)
        constraints = []
        
        day_map = {
            'monday': 'Mon', 'tuesday': 'Tue', 'wednesday': 'Wed',
            'thursday': 'Thu', 'friday': 'Fri', 'saturday': 'Sat', 'sunday': 'Sun',
            'mon': 'Mon', 'tue': 'Tue', 'wed': 'Wed', 'thu': 'Thu', 'fri': 'Fri'
        }

        for ent in entities:
            label = ent["label"]
            val = ent["text"]
            val_lower = val.lower()
            
            if label == "time":
                hour = self.extract_hour(val_lower)
                if hour is not None:
                    # Look at context to determine direction
                    start_pos = ent["start"]
                    # Catch context window
                    context_before = text[max(0, start_pos-80):start_pos].lower()
                    
                    # Keywords for AFTER (latest limit)
                    after_keywords = ["after", "past", "done by", "finish by", "end by", "late", "by "]
                    # Keywords for BEFORE (earliest limit)
                    before_keywords = ["before", "until", "earlier", "early", "start after"]
                    
                    is_negative = any(neg in context_before for neg in ["no ", "not ", "don't ", "dont ", "avoid ", "can't ", "cant "])
                    
                    # Check for "done by", "finish by", etc. first
                    if any(kw in context_before for kw in ["done by", "finish by", "end by", "by "]):
                        constraints.append({"type": "no_classes_after", "time": hour})
                    elif "after" in context_before:
                        # Find the last "after" in context_before
                        last_after_idx = context_before.rfind("after")
                        text_around_after = context_before[max(0, last_after_idx-15):last_after_idx+5]
                        
                        is_neg_near_after = any(neg in text_around_after for neg in ["no ", "not ", "don't ", "dont ", "avoid ", "can't ", "cant "])
                        
                        if is_neg_near_after or "nothing" in context_before:
                            constraints.append({"type": "no_classes_after", "time": hour})
                        else:
                            # "Classes after 4pm" -> starts after 4pm -> no classes before 4pm
                            constraints.append({"type": "no_classes_before", "time": hour})
                    elif any(kw in context_before for kw in ["past", "late"]):
                        constraints.append({"type": "no_classes_after", "time": hour})
                    elif any(kw in context_before for kw in before_keywords):
                        # "no classes before 10am" -> before
                        # "before 10am" -> before
                        constraints.append({"type": "no_classes_before", "time": hour})
                    else:
                        # Fallback based on hour if ambiguous
                        if hour < 12:
                            # If it's a small hour like "1", it's probably afternoon (1pm) if not specified
                            # But if the user says "classes after 1", they mean 1pm.
                            # For the purpose of the scheduler, hours 1-6 are often PM.
                            if 1 <= hour <= 7 and "am" not in val_lower:
                                # Only adjust if "pm" isn't explicitly there but implied by "late" or high probability
                                if any(kw in context_before for kw in ["late", "evening", "afternoon"]):
                                    hour += 12
                            
                            if hour < 12:
                                constraints.append({"type": "no_classes_before", "time": hour})
                            else:
                                constraints.append({"type": "no_classes_after", "time": hour})
                        else:
                            constraints.append({"type": "no_classes_after", "time": hour})
            
            elif label == "day":
                for full_day, abbrev in day_map.items():
                    if full_day in val_lower:
                        constraints.append({"type": "no_day", "day": abbrev})
                        break
            
            elif label == "person name":
                # Filter out single letters or common pronouns misidentified as names
                if len(val_lower.strip()) < 2 or val_lower.strip() in ["i", "me", "my", "ta"]:
                    continue
                    
                ta_name = re.sub(r'\b(ta|teaching assistant)\b', '', val_lower, flags=re.IGNORECASE).strip()
                if ta_name:
                    constraints.append({"type": "avoid_ta", "name": ta_name.title()})

        print(f"🔍 GLINER PARSER: Found {len(constraints)} constraints")
        return {
            "constraints": constraints,
            "raw_entities": entities
        }
