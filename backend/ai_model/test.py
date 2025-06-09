from spacy.tokens import DocBin
import spacy
from spacy.training.example import Example

def validate_data(nlp, train_data):
    print("\nValidating training data...")
    for text, annotations in train_data:
        try:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
        except Exception as e:
            print(f"❌ Error in example:\nText: {text}\nAnnotations: {annotations}\nError: {e}")

# Example usage
from train_ner import TRAIN_DATA  # Update to your actual import
nlp = spacy.blank("en")
validate_data(nlp, TRAIN_DATA)
