from src.statement_analysis.parser import parse_sentence_to_claim


sentence = "The person was at home at 6:30 PM."

claim = parse_sentence_to_claim(
    statement_id="STMT_NLP_001",
    sentence=sentence,
)

print("Generated claim:")
print(claim.model_dump())

assert claim.start_time.hour == 18
assert claim.start_time.minute == 30
assert claim.location == "home"

print("\nPASS: Natural-language sentence converted to Claim.")