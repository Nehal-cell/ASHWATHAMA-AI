from src.statement_analysis.parser import parse_statement_text


statement = """
The person left home at 6 PM.
They arrived at the office at 7 PM.
They stayed at the office until 9 PM.
"""

claims = parse_statement_text(
    statement_id="STMT_NLP_003",
    statement=statement,
)

print("Generated claims:")

for claim in claims:
    print(claim.model_dump())

assert len(claims) == 3

assert claims[0].action == "left"
assert claims[0].location == "home"
assert claims[0].start_time.hour == 18

assert claims[1].action == "arrived"
assert claims[1].location == "office"
assert claims[1].start_time.hour == 19

assert claims[2].action == "stayed"
assert claims[2].location == "office"

print("\nPASS: Complete statement converted into multiple claims.")