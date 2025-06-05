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
        doc = self.nlp(text)
        constraints = []

        for ent in doc.ents:
            if ent.label_ == "NO_CLASS_BEFORE":
                # Try to extract the hour from the entity text
                hour_text = ent.text.strip().lower().replace("am", "").replace("pm", "").strip()
                try:
                    hour = int(hour_text)
                    if "pm" in ent.text.lower() and hour < 12:
                        hour += 12
                    if "am" in ent.text.lower() and hour == 12:
                        hour = 0
                except ValueError:
                    hour = None

                if hour is not None:
                    constraints.append({
                        "type": "no_early_classes",
                        "time": hour
                    })

            elif ent.label_ == "NO_CLASS_DAY":
                constraints.append({
                    "type": "no_day",
                    "day": ent.text.strip().capitalize()[:3]  # e.g., Tuesday -> Tue
                })

        return {
            "constraints": constraints
        }