from src.statement_analysis.extractor import extract_subject_action
from src.statement_analysis.parser import parse_sentence_to_claim


sentence = "The person left home at 6:30 PM."

subject, action = extract_subject_action(sentence)

print("Subject:", subject)
print("Action:", action)

assert subject == "the person"
assert action == "left"


claim = parse_sentence_to_claim(
    statement_id="STMT_NLP_002",
    sentence=sentence,
)

print("\nGenerated claim:")
print(claim.model_dump())

assert claim.subject == "the person"
assert claim.action == "left"
assert claim.location == "home"
assert claim.start_time.hour == 18
assert claim.start_time.minute == 30

print("\nPASS: Subject and action extraction works.")