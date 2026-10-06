from src.statement_analysis.extractor import extract_end_time


def test_extract_end_time():
    result = extract_end_time(
        "They stayed at the office until 9 PM."
    )

    assert result is not None
    assert result.hour == 21
    assert result.minute == 0