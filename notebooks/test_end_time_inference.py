from src.statement_analysis.parser import parse_statement_text


def test_end_time_inference_from_previous_claim():
    statement = (
        "The person left home at 6 PM. "
        "They arrived at the office at 7 PM. "
        "They stayed at the office until 9 PM."
    )

    claims = parse_statement_text(
        statement_id="STMT_TIME_001",
        statement=statement,
    )

    assert len(claims) == 3

    stayed_claim = claims[2]

    assert stayed_claim.subject == "the person"
    assert stayed_claim.action == "stayed"
    assert stayed_claim.location == "office"

    assert stayed_claim.start_time is not None
    assert stayed_claim.end_time is not None

    assert stayed_claim.start_time.hour == 19
    assert stayed_claim.start_time.minute == 0

    assert stayed_claim.end_time.hour == 21
    assert stayed_claim.end_time.minute == 0