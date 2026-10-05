from datetime import datetime

from src.statement_analysis.parser import create_claim


claim = create_claim(
    claim_id="CL_001",
    statement_id="STMT_001",
    subject="person",
    action="left",
    start_time=datetime(2026, 1, 15, 18, 0),
    location="home",
    description="The person stated that they left home at 6 PM.",
)


print("Statement parser test:")
print(claim.model_dump())