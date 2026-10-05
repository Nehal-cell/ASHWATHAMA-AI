from datetime import datetime

from src.statement_analysis.claim_schema import Claim
from src.statement_analysis.text_processor import split_sentences
from src.statement_analysis.extractor import (
    extract_location,
    extract_subject_action,
    extract_time,
)


def create_claim(
    claim_id: str,
    statement_id: str,
    subject: str,
    action: str,
    description: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    location: str | None = None,
    object: str | None = None,
    expected: bool | None = None,
) -> Claim:
    """
    Create a validated Claim object.
    """

    return Claim(
        claim_id=claim_id,
        statement_id=statement_id,
        subject=subject,
        action=action,
        start_time=start_time,
        end_time=end_time,
        location=location,
        object=object,
        expected=expected,
        description=description,
    )


def parse_statement(
    statement_id: str,
    extracted_claims: list[dict],
) -> list[Claim]:
    """
    Convert manually extracted claim dictionaries
    into validated Claim objects.
    """

    claims = []

    for index, data in enumerate(extracted_claims, start=1):
        claim = create_claim(
            claim_id=data.get(
                "claim_id",
                f"{statement_id}_CL_{index:03d}",
            ),
            statement_id=statement_id,
            subject=data["subject"],
            action=data["action"],
            description=data["description"],
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            location=data.get("location"),
            object=data.get("object"),
            expected=data.get("expected"),
        )

        claims.append(claim)

    return claims


def parse_sentence_to_claim(
    statement_id: str,
    sentence: str,
    claim_number: int = 1,
) -> Claim:
    """
    Convert a natural-language sentence into
    an initial structured Claim.
    """

    start_time = extract_time(sentence)
    location = extract_location(sentence)

    subject, action = extract_subject_action(sentence)

    return create_claim(
        claim_id=f"{statement_id}_CL_{claim_number:03d}",
        statement_id=statement_id,
        subject=subject or "unknown",
        action=action or "unknown",
        description=sentence,
        start_time=start_time,
        location=location,
    )

def parse_statement_text(
    statement_id: str,
    statement: str,
) -> list[Claim]:
    """
    Convert a complete natural-language statement
    into multiple structured Claim objects.
    """

    sentences = split_sentences(statement)

    claims = []

    for index, sentence in enumerate(sentences, start=1):
        claim = parse_sentence_to_claim(
            statement_id=statement_id,
            sentence=sentence,
            claim_number=index,
        )

        claims.append(claim)

    return claims