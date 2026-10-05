from datetime import datetime

from src.statement_analysis.parser import parse_statement


extracted_claims = [
    {
        "subject": "person",
        "action": "left",
        "start_time": datetime(2026, 1, 15, 18, 0),
        "location": "home",
        "description": "The person stated that they left home at 6 PM.",
    },
    {
        "subject": "person",
        "action": "arrived",
        "start_time": datetime(2026, 1, 15, 19, 0),
        "location": "office",
        "description": "The person stated that they arrived at the office at 7 PM.",
    },
]


claims = parse_statement(
    statement_id="STMT_001",
    extracted_claims=extracted_claims,
)


print("Parsed claims:")

for claim in claims:
    print(claim.model_dump())

print(f"\nTotal claims: {len(claims)}")