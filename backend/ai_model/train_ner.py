import spacy
from spacy.training.example import Example
from training_data import TRAIN_DATA

# Create blank English model
nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Add labels
ner.add_label("NO_CLASS_BEFORE")
ner.add_label("NO_CLASS_DAY")

# Initialize model
nlp.initialize()

# Training
for epoch in range(30):
    losses = {}
    for text, annotations in TRAIN_DATA:
        example = Example.from_dict(nlp.make_doc(text), annotations)
        nlp.update([example], losses=losses)
    print(f"Epoch {epoch} Losses", losses)

# Save the model
nlp.to_disk("schedule_ner")
