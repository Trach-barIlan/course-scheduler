import pytest
from unittest.mock import Mock, patch
import spacy
from ai_model.ml_parser import ScheduleParser

class TestScheduleParser:
    """Test cases for the ScheduleParser class."""

    @pytest.fixture
    def mock_nlp_model(self):
        """Mock spaCy NLP model."""
        with patch('spacy.load') as mock_load:
            mock_nlp = Mock()
            mock_doc = Mock()
            mock_doc.ents = []
            mock_nlp.return_value = mock_doc
            mock_load.return_value = mock_nlp
            yield mock_nlp
    
    def test_parse_basic(self, mock_nlp_model):
        """Test basic constraint parsing."""
        parser = ScheduleParser()
        constraints = "No classes before 9am"
        result = parser.parse(constraints)
        assert isinstance(result, dict)
        assert "constraints" in result
        assert "raw_entities" in result
    
    def test_parse_complex(self, mock_nlp_model):
        """Test complex constraint parsing."""
        parser = ScheduleParser()
        constraints = "No early morning classes before 10am and not on Tuesday, avoid TA Brown"
        result = parser.parse(constraints)
        assert isinstance(result, dict)
        assert "constraints" in result
        assert "raw_entities" in result
    
    def test_parse_empty(self, mock_nlp_model):
        """Test parsing empty constraints."""
        parser = ScheduleParser()
        result = parser.parse("")
        assert isinstance(result, dict)
        assert result["constraints"] == []
        assert isinstance(result["raw_entities"], list)
    
    def test_raw_entities(self, mock_nlp_model):
        """Test entity extraction from text."""
        # Mock entities
        mock_entity1 = Mock()
        mock_entity1.text = "9am"
        mock_entity1.label_ = "NO_CLASS_BEFORE"
        mock_entity1.start_char = 17
        mock_entity1.end_char = 20
        
        mock_entity2 = Mock()
        mock_entity2.text = "Tuesday"
        mock_entity2.label_ = "NO_CLASS_DAY"
        mock_entity2.start_char = 24
        mock_entity2.end_char = 31
        
        mock_doc = Mock()
        mock_doc.ents = [mock_entity1, mock_entity2]
        mock_nlp_model.return_value = mock_doc
        
        parser = ScheduleParser()
        result = parser.parse("No classes before 9am on Tuesday")
        entities = result["raw_entities"]
        assert len(entities) == 2
        assert entities[0]["text"] == "9am"
        assert entities[0]["label"] == "NO_CLASS_BEFORE"
        assert entities[1]["text"] == "Tuesday"
        assert entities[1]["label"] == "NO_CLASS_DAY"

class TestNERModel:
    """Test cases for the NER model functionality."""
    
    @pytest.fixture
    def mock_spacy_model(self):
        """Mock spaCy model for testing."""
        with patch('spacy.load') as mock_load:
            mock_nlp = Mock()
            
            # Mock document processing
            def mock_process(text):
                mock_doc = Mock()
                mock_doc.text = text
                mock_doc.ents = []
                return mock_doc
            
            mock_nlp.side_effect = mock_process
            mock_load.return_value = mock_nlp
            yield mock_nlp
    
    def test_ner_model_loading(self, mock_spacy_model):
        """Test NER model loading."""
        from ai_model.ml_parser import ScheduleParser
        
        parser = ScheduleParser()
        assert parser.nlp is not None
    
    def test_ner_entity_recognition(self, mock_spacy_model):
        """Test NER entity recognition."""
        # Mock entities
        mock_time_entity = Mock()
        mock_time_entity.text = "9am"
        mock_time_entity.label_ = "TIME"
        mock_time_entity.start_char = 17
        mock_time_entity.end_char = 20
        
        mock_day_entity = Mock()
        mock_day_entity.text = "Monday"
        mock_day_entity.label_ = "DAY"
        mock_day_entity.start_char = 24
        mock_day_entity.end_char = 30
        
        def mock_process(text):
            mock_doc = Mock()
            mock_doc.text = text
            mock_doc.ents = [mock_time_entity, mock_day_entity]
            return mock_doc
        
        mock_spacy_model.side_effect = mock_process
        
        parser = ScheduleParser()
        result = parser.parse("No classes before 9am on Monday")
        entities = result["raw_entities"]
        assert len(entities) == 2
        assert entities[0]["text"] == "9am"
        assert entities[0]["label"] == "TIME"
        assert entities[1]["text"] == "Monday"
        assert entities[1]["label"] == "DAY"
    
    def test_ner_no_entities(self, mock_spacy_model):
        """Test NER when no entities are found."""
        def mock_process(text):
            mock_doc = Mock()
            mock_doc.text = text
            mock_doc.ents = []
            return mock_doc
        
        mock_spacy_model.side_effect = mock_process
        
        from ai_model.ml_parser import ScheduleParser
        parser = ScheduleParser()
        result = parser.parse("No specific constraints")
        entities = result["raw_entities"]
        assert len(entities) == 0

class TestConstraintIntegration:
    """Integration tests for constraint parsing."""
    
    # def test_full_constraint_parsing_pipeline(self):
    #     """Test the full constraint parsing pipeline."""
    #     from ai_model.ml_parser import ScheduleParser
        
    #     parser = ScheduleParser()
    #     constraints = "No classes before 9am and no Friday classes, avoid TA Smith"
        
    #     # Mock the NER output to include a NO_CLASS_DAY entity for Friday
    #     with patch.object(parser.nlp, '__call__') as mock_call:
    #         mock_day_entity = Mock()
    #         mock_day_entity.text = "Friday"
    #         mock_day_entity.label_ = "NO_CLASS_DAY"
    #         mock_day_entity.start_char = 0
    #         mock_day_entity.end_char = 6
    #         mock_ta_entity = Mock()
    #         mock_ta_entity.text = "TA Smith"
    #         mock_ta_entity.label_ = "AVOID_TA"
    #         mock_ta_entity.start_char = 30
    #         mock_ta_entity.end_char = 38
    #         mock_doc = Mock()
    #         mock_doc.ents = [mock_day_entity, mock_ta_entity]
    #         mock_call.return_value = mock_doc
    #         result = parser.parse(constraints)
    #         assert isinstance(result, dict)
    #         assert "constraints" in result
    #         assert "raw_entities" in result
    #         print("Result constraints:", result["constraints"])
    #         print("Result raw_entities:", result["raw_entities"])
    #         # Debug: print constraint types
    #         for c in result["constraints"]:
    #             print("Constraint type:", c.get("type"), "day:", c.get("day"), "name:", c.get("name"))
    #         day_constraints = [c for c in result["constraints"] if c.get("type") == "no_day" or c.get("type") == "NO_DAY"]
    #         ta_constraints = [c for c in result["constraints"] if c.get("type") == "avoid_ta" or c.get("type") == "AVOID_TA"]
    #         assert len(day_constraints) > 0, f"No day constraints found: {result['constraints']}"
    #         assert len(ta_constraints) > 0, f"No TA constraints found: {result['constraints']}"
    
    def test_constraint_parsing_edge_cases(self):
        """Test constraint parsing with edge cases."""
        
        parser = ScheduleParser()
        
        # Test with very long constraints
        long_constraints = "No classes before 9am and no classes after 6pm and no classes on Monday Tuesday Wednesday Thursday Friday and avoid TA Smith TA Johnson TA Brown and prefer TA Wilson"
        result = parser.parse(long_constraints)
        
        assert isinstance(result, dict)
        assert "constraints" in result
        assert "raw_entities" in result
        
        # Test with special characters
        special_constraints = "No classes before 9am! And no Friday classes? Avoid TA Smith."
        result = parser.parse(special_constraints)
        
        assert isinstance(result, dict)
        
        # Test with numbers in text
        numeric_constraints = "No classes before 9am and I have 5 courses to schedule"
        result = parser.parse(numeric_constraints)
        
        assert isinstance(result, dict)