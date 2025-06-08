from spacy.training.iob_utils import offsets_to_biluo_tags
import spacy

nlp = spacy.blank("en")

text = "Avoid 7:30am and Friday sessions"
entities = [(32, 36, "NO_CLASS_BEFORE")]  # Example from your data

doc = nlp.make_doc(text)
tags = offsets_to_biluo_tags(doc, entities)
print(tags)

print("--------------real-----------------")
for i, token in enumerate(nlp(text)):
    print(f"{i}: {token.text} [{token.idx}-{token.idx+len(token.text)}]")