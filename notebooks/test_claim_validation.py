from datetime import datetime

from pydantic import ValidationError

from src.statement_analysis.claim_schema import Claim


# -------------------------
# Test 1: Valid claim
# -------------------------

valid_claim = Claim(
    claim_id="CL_001",
    statement_id="STMT_001",
    subject="person",
    action="left",
    start_time=datetime(2026, 1, 15, 18, 0),
    end_time=datetime(2026, 1, 15, 18, 30),
    location="home",
    description="The person stated that they left home at 6 PM.",
)

print("PASS: Valid claim accepted.")
print(valid_claim.model_dump())


# -------------------------
# Test 2: Invalid time range
# -------------------------

try:
    Claim(
        claim_id="CL_002",
        statement_id="STMT_001",
        subject="person",
        action="left",
        start_time=datetime(2026, 1, 15, 19, 0),
        end_time=datetime(2026, 1, 15, 18, 0),
        location="home",
        description="Invalid time range.",
    )

    print("FAIL: Invalid time range was accepted.")

except (ValidationError, ValueError):
    print("PASS: Invalid time range rejected.")


# -------------------------
# Test 3: Empty subject
# -------------------------

try:
    Claim(
        claim_id="CL_003",
        statement_id="STMT_001",
        subject="   ",
        action="left",
        description="Claim with empty subject.",
    )

    print("FAIL: Empty subject was accepted.")

except (ValidationError, ValueError):
    print("PASS: Empty subject rejected.")