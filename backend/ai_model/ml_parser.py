import spacy
from typing import Dict, List, Any
import re
import os

class ScheduleParser:
    def __init__(self):
        model_path = os.path.join(
            os.path.dirname(__file__),  # Changed to look in ai_model directory
            "schedule_ner"
        )
        if not os.path.exists(model_path):
            raise IOError(f"Model not found at {model_path}")
        self.nlp = spacy.load(model_path)
        print(f"Successfully loaded model from {model_path}")

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse text to extract scheduling constraints."""
        # Preprocess text to handle case sensitivity
        normalized_text = text.lower()
        doc = self.nlp(normalized_text)
        constraints = []
        
        for ent in doc.ents:
            if ent.label_ == "NO_CLASS_BEFORE" or ent.label_ == "NO_CLASS_AFTER":
                # Try to extract the hour from the entity text
                hour_text = ent.text.strip().lower()
                
                # Handle special cases
                if "noon" in hour_text:
                    hour = 12
                elif "midnight" in hour_text:
                    hour = 0
                else:
                    # Remove am/pm and extra spaces
                    hour_text = hour_text.replace("am", "").replace("pm", "").strip()
                    try:
                        # Handle both whole hours and times with minutes
                        if ":" in hour_text:
                            hour, minute = map(int, hour_text.split(":"))
                        else:
                            hour = int(hour_text)
                            minute = 0
                        
                        # Adjust for PM times
                        if "pm" in ent.text.lower() and hour < 12:
                            hour += 12
                        # Adjust for 12 AM
                        if "am" in ent.text.lower() and hour == 12:
                            hour = 0
                            
                        if ent.label_ == "NO_CLASS_BEFORE":
                            constraints.append({
                                "type": "no_classes_before",
                                "time": hour
                            })
                        elif ent.label_ == "NO_CLASS_AFTER":
                            constraints.append({
                                "type": "no_classes_after",
                                "time": hour
                            })
                    except ValueError:
                        print(f"Could not parse time from: {hour_text}")
                        continue

            elif ent.label_ == "NO_CLASS_DAY":
                # Handle day names case-insensitively
                day_map = {
                    'monday': 'Mon',
                    'tuesday': 'Tue',
                    'wednesday': 'Wed',
                    'thursday': 'Thu',
                    'friday': 'Fri'
                }
                day_text = ent.text.strip().lower()
                for day_name, abbrev in day_map.items():
                    if day_name in day_text:
                        constraints.append({
                            "type": "no_day",
                            "day": abbrev
                        })
                        break

            elif ent.label_ == "AVOID_TA":
                ta_name = ent.text.replace("ta", "").replace("TA", "").strip()
                if ta_name:
                    constraints.append({
                        "type": "avoid_ta",
                        "name": ta_name
                    })
            

        return {
            "constraints": constraints,
            "raw_entities": [
                {
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                } for ent in doc.ents
            ]
        }