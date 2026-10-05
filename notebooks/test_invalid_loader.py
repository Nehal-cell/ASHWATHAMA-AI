from src.evidence.loader import load_evidence

try:
    load_evidence("data/sample/evidence_invalid.json")
    print("ERROR: Invalid evidence was accepted!")
except ValueError as error:
    print("PASS: Loader rejected invalid evidence.")
    print(error)