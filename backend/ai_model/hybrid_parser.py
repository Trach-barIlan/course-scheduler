import spacy
from spacy.matcher import Matcher
from spacy.lang.en import English
import re
from typing import Dict, List, Any
from datetime import datetime

class HybridScheduleParser:
    """
    Advanced parser that combines rule-based patterns with ML for better accuracy
    """
    
    def __init__(self):
        # Load base English model
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)
        
        # Add sophisticated rule-based patterns
        self._add_time_patterns()
        self._add_day_patterns()
        self._add_ta_patterns()
        
    def _add_time_patterns(self):
        """Add comprehensive time constraint patterns"""
        
        # Before patterns
        before_patterns = [
            [{"LOWER": {"IN": ["no", "not", "avoid", "don't", "dont"]}}, 
             {"LOWER": {"IN": ["classes", "class", "sessions"]}}, 
             {"LOWER": "before"}, 
             {"SHAPE": {"IN": ["d", "dd", "d:dd"]}, "OP": "?"}, 
             {"LOWER": {"IN": ["am", "pm"]}, "OP": "?"}],
            
            [{"LOWER": {"IN": ["nothing", "no", "avoid"]}}, 
             {"LOWER": "before"}, 
             {"SHAPE": {"IN": ["d", "dd", "d:dd", "dd:dd"]}, "OP": "?"}, 
             {"LOWER": {"IN": ["am", "pm", "noon", "midnight"]}, "OP": "?"}],
            
            [{"LOWER": {"IN": ["after", "past"]}}, 
             {"SHAPE": {"IN": ["d", "dd", "d:dd", "dd:dd"]}, "OP": "?"}, 
             {"LOWER": {"IN": ["am", "pm", "noon", "midnight"]}, "OP": "?"}],
        ]
        
        # After patterns  
        after_patterns = [
            [{"LOWER": {"IN": ["no", "not", "avoid", "don't", "dont"]}}, 
             {"LOWER": {"IN": ["classes", "class", "sessions"]}}, 
             {"LOWER": "after"}, 
             {"SHAPE": {"IN": ["d", "dd", "d:dd", "dd:dd"]}, "OP": "?"}, 
             {"LOWER": {"IN": ["am", "pm"]}, "OP": "?"}],
            
            [{"LOWER": {"IN": ["nothing", "no", "avoid"]}}, 
             {"LOWER": "after"}, 
             {"SHAPE": {"IN": ["d", "dd", "d:dd", "dd:dd"]}, "OP": "?"}, 
             {"LOWER": {"IN": ["am", "pm", "noon", "midnight"]}, "OP": "?"}],
            
            [{"LOWER": "before"}, 
             {"SHAPE": {"IN": ["d", "dd", "d:dd", "dd:dd"]}, "OP": "?"}, 
             {"LOWER": {"IN": ["am", "pm", "noon", "midnight"]}, "OP": "?"}],
        ]
        
        self.matcher.add("TIME_BEFORE", before_patterns)
        self.matcher.add("TIME_AFTER", after_patterns)
        
    def _add_day_patterns(self):
        """Add day constraint patterns"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", 
                "mon", "tue", "wed", "thu", "fri"]
        
        day_patterns = [
            [{"LOWER": {"IN": ["no", "not", "avoid", "don't", "dont"]}}, 
             {"LOWER": {"IN": ["classes", "class"]}}, 
             {"LOWER": "on", "OP": "?"}, 
             {"LOWER": {"IN": days}}],
            
            [{"LOWER": {"IN": ["no", "avoid"]}}, 
             {"LOWER": {"IN": days}}],
        ]
        
        self.matcher.add("DAY_CONSTRAINT", day_patterns)
        
    def _add_ta_patterns(self):
        """Add TA constraint patterns"""
        ta_patterns = [
            [{"LOWER": {"IN": ["avoid", "not", "no", "don't", "dont"]}}, 
             {"LOWER": "ta"}, 
             {"IS_ALPHA": True, "OP": "+"}],
            
            [{"LOWER": {"IN": ["avoid", "not"]}}, 
             {"IS_ALPHA": True, "OP": "+"}, 
             {"LOWER": "as"}, 
             {"LOWER": "ta"}],
        ]
        
        self.matcher.add("TA_CONSTRAINT", ta_patterns)
    
    def _extract_time(self, text: str) -> int:
        """Enhanced time extraction using multiple methods"""
        text = text.lower().strip()
        
        # Handle special cases
        if "noon" in text:
            return 12
        if "midnight" in text:
            return 0
            
        # Regex patterns for time extraction
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',  # 9:30am, 2:15
            r'(\d{1,2})\s*(am|pm)',          # 9am, 2pm
            r'(\d{1,2})',                    # 9, 12
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                period = match.group(-1) if len(match.groups()) > 2 else None
                
                # Adjust for AM/PM
                if period == "pm" and hour < 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                    
                return hour
        
        return None
    
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse text using hybrid approach"""
        doc = self.nlp(text)
        matches = self.matcher(doc)
        constraints = []
        
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            
            if label == "TIME_BEFORE":
                time = self._extract_time(span.text)
                if time is not None:
                    constraints.append({
                        "type": "no_classes_before",
                        "time": time,
                        "confidence": 0.9,
                        "matched_text": span.text
                    })
            
            elif label == "TIME_AFTER":
                time = self._extract_time(span.text)
                if time is not None:
                    constraints.append({
                        "type": "no_classes_after",
                        "time": time,
                        "confidence": 0.9,
                        "matched_text": span.text
                    })
            
            elif label == "DAY_CONSTRAINT":
                day_map = {
                    'monday': 'Mon', 'tuesday': 'Tue', 'wednesday': 'Wed',
                    'thursday': 'Thu', 'friday': 'Fri',
                    'mon': 'Mon', 'tue': 'Tue', 'wed': 'Wed',
                    'thu': 'Thu', 'fri': 'Fri'
                }
                
                for day_name, abbrev in day_map.items():
                    if day_name in span.text.lower():
                        constraints.append({
                            "type": "no_day",
                            "day": abbrev,
                            "confidence": 0.95,
                            "matched_text": span.text
                        })
                        break
            
            elif label == "TA_CONSTRAINT":
                ta_name = re.sub(r'\b(avoid|not|no|don\'t|dont|ta)\b', '', span.text, flags=re.IGNORECASE).strip()
                if ta_name:
                    constraints.append({
                        "type": "avoid_ta",
                        "name": ta_name,
                        "confidence": 0.85,
                        "matched_text": span.text
                    })
        
        return {
            "constraints": constraints,
            "raw_matches": [
                {
                    "text": doc[start:end].text,
                    "label": self.nlp.vocab.strings[match_id],
                    "start": start,
                    "end": end
                } for match_id, start, end in matches
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    parser = HybridScheduleParser()
    
    test_sentences = [
        "No classes before 9am",
        "I can't attend anything after 5:30pm",
        "Avoid classes on Friday",
        "Don't schedule TA Smith",
        "No early morning classes before 10:30",
        "Nothing after 4 please",
        "Avoid TA Johnson for CS101"
    ]
    
    for sentence in test_sentences:
        result = parser.parse(sentence)
        # Example output would be:
        # Input: No early morning classes before 10:30
        # Constraints: [{"type": "no_classes_before", "time": 10}]
