import spacy
from spacy.training.example import Example
from training_data import TRAIN_DATA
from test_data import TEST_DATA
from patterns import PATTERNS  # Assuming you have a patterns.py file with your entity patterns
import random
import os
from spacy.util import minibatch, compounding
from spacy.scorer import Scorer
from collections import defaultdict

def calculate_accuracy(nlp, test_data):
    correct = 0
    total = 0
    
    print("\nEvaluating on test data:")
    for text, annotations in test_data:
        doc = nlp(text)
        expected_entities = set([
            (start, end, label) 
            for start, end, label in annotations["entities"]
        ])
        predicted_entities = set([
            (ent.start_char, ent.end_char, ent.label_) 
            for ent in doc.ents
        ])
        
        # Print each test case result
        print(f"\nText: {text}")
        print(f"Expected: {expected_entities}")
        print(f"Predicted: {predicted_entities}")
        
        # Count correct predictions
        correct += len(expected_entities.intersection(predicted_entities))
        total += len(expected_entities)
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"\nAccuracy: {accuracy:.2f}% ({correct}/{total} entities correctly identified)")
    return accuracy

def per_label_accuracy(nlp, test_data):
    correct = defaultdict(int)
    total = defaultdict(int)

    for text, ann in test_data:
        expected = {(start, end, label) for start, end, label in ann["entities"]}
        predicted = {(ent.start_char, ent.end_char, ent.label_) for ent in nlp(text).ents}
        
        for _, _, label in ann["entities"]:
            total[label] += 1

        for ent in expected & predicted:
            correct[ent[2]] += 1

    for label in total:
        acc = (correct[label] / total[label]) * 100 if total[label] else 0
        print(f"{label}: {acc:.2f}% ({correct[label]}/{total[label]})")

def add_pattern_matching(nlp):
    # Create an entity ruler and add it BEFORE the NER component
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    # Add patterns to the ruler
    ruler.add_patterns(PATTERNS)

def preprocess_text(nlp, text):
    """Normalize text before processing."""
    # First, preserve existing capitalization
    doc = nlp.make_doc(text)
    
    # Replace day names with title case version
    day_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    normalized = text
    for day in day_names:
        # Replace full lowercase or uppercase versions with title case
        normalized = normalized.replace(day.lower(), day.title())
        normalized = normalized.replace(day.upper(), day.title())
    
    return normalized

def train_ner():
    # Create blank English model
    nlp = spacy.load("en_core_web_md")
    
    # Remove existing pipes we'll recreate
    if "ner" in nlp.pipe_names:
        nlp.remove_pipe("ner")
    if "entity_ruler" in nlp.pipe_names:
        nlp.remove_pipe("entity_ruler")
        
    # Add NER and pattern matching in correct order
    ner = nlp.add_pipe("ner", last=True)
    #add_pattern_matching(nlp)

    # Add labels and prepare for transfer learning
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    
    # Print label distribution for monitoring
    label_counts = {}
    for _, annotations in TRAIN_DATA:
        for _, _, label in annotations.get("entities"):
            label_counts[label] = label_counts.get(label, 0) + 1
    print("\nLabel distribution in training data:")
    for label, count in label_counts.items():
        print(f"{label}: {count} examples")

    # Get names of other pipes to disable during training
    pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes):
        # Initialize the model with transfer learning settings
        optimizer = nlp.begin_training()
        optimizer.learn_rate = 0.002
        
        # Training parameters optimized for transfer learning
        n_iter = 50  # Fewer iterations needed with pre-trained model
        batch_size = 8
        drop_rate = 0.1  # Lower dropout for stability
        patience = 5  # Number of evaluations without improvement before stopping
        best_accuracy = 0  # Track best accuracy for early stopping
        best_model = None
        no_improve = 0
        
        # Use compound batches for better learning
        sizes = compounding(batch_size, 32.0, 1.001)
        
        # Training loop
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            batches = list(minibatch(TRAIN_DATA, size=sizes))
            losses = {}
            
            # Update for each batch
            for batch in batches:
                for text, annotations in batch:
                    processed_text = preprocess_text(nlp, text)
                    doc = nlp.make_doc(processed_text)
                    example = Example.from_dict(doc, annotations)
                    nlp.update([example], drop=drop_rate, losses=losses)
                    
            # Evaluate every 10 iterations (more frequent with fewer total iterations)
            if itn % 10 == 0:
                print(f"\nIteration #{itn}")
                print(f"Losses: {losses}")
                
                # Calculate accuracy per label silently
                with open(os.devnull, 'w') as f:
                    # Temporarily redirect stdout
                    import sys
                    old_stdout = sys.stdout
                    sys.stdout = f
                    interim_accuracy = calculate_accuracy(nlp, TEST_DATA)
                    sys.stdout = old_stdout
                
                print(f"Current accuracy: {interim_accuracy:.2f}%")
                
                # Early stopping check
                if interim_accuracy > best_accuracy:
                    best_accuracy = interim_accuracy
                    best_model = nlp.to_bytes()  # Store model in memory
                    no_improve = 0
                else:
                    no_improve += 1
                    if no_improve >= patience:
                        print("\nStopping early: no improvement in accuracy")
                        break

        # Load best model from memory for final evaluation
        if best_model is not None:
            nlp.from_bytes(best_model)

        print("\n--- Final Evaluation ---")
        final_accuracy = calculate_accuracy(nlp, TEST_DATA)
        print("\n--- Per Label Accuracy ---")
        per_label_accuracy(nlp, TEST_DATA)
        
        # Save only the final best model
        output_dir = os.path.join(os.path.dirname(__file__), "schedule_ner")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        nlp.to_disk(output_dir)
        print(f"\nBest model saved with accuracy: {best_accuracy:.2f}%")

if __name__ == "__main__":
    train_ner()
