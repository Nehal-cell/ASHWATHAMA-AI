from datetime import datetime

from src.statement_analysis.claim_schema import Claim


claim = Claim(
    claim_id="CL_001",
    statement_id="STMT_001",
    subject="person",
    action="left",
    start_time=datetime(2026, 1, 15, 18, 0),
    location="home",
    description="The person stated that they left home at 6 PM.",
)


print("Claim created successfully:")
print(claim.model_dump())