from src.statement_analysis.text_processor import (
    clean_statement,
    split_sentences,
)


statement = """
The person left home at 6 PM.
They arrived at the office at 7 PM.
They stayed there until 9 PM.
"""

cleaned = clean_statement(statement)
sentences = split_sentences(statement)

print("Cleaned statement:")
print(cleaned)

print("\nSentences:")
for index, sentence in enumerate(sentences, start=1):
    print(f"{index}. {sentence}")

assert len(sentences) == 3
assert sentences[0] == "The person left home at 6 PM."
assert sentences[1] == "They arrived at the office at 7 PM."
assert sentences[2] == "They stayed there until 9 PM."

print("\nPASS: Statement text processing works.")