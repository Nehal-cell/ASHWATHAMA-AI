from src.statement_analysis.parser import parse_statement_text


def test_pronoun_resolution():
    statement = (
        "The person left home at 6 PM. "
        "They arrived at the office at 7 PM."
    )

    claims = parse_statement_text(
        statement_id="ST_001",
        statement=statement,
    )

    assert len(claims) == 2

    assert claims[0].subject == "the person"
    assert claims[1].subject == "the person"