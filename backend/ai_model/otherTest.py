import spacy
from test_data import TEST_DATA  # Make sure test_data is a list of strings

nlp = spacy.blank("en")

for idx, (text, annotation) in enumerate(TEST_DATA):
    print(f"\n[{idx+1}] {text}")
    for i, token in enumerate(nlp(text)):
        print(f"{i}: {token.text} [{token.idx}-{token.idx + len(token.text)}]")
    print(f"--------------DONE {idx+1}-----------------")
