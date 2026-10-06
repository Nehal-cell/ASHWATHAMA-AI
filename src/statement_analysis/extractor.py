import re
from datetime import datetime


def extract_time(text: str) -> datetime | None:
    """
    Extract a simple clock time from statement text.

    Examples:
        6 PM
        6:30 PM
        18:30
    """

    pattern = r"\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)\b"

    match = re.search(pattern, text)

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    period = match.group(3).upper()

    if hour < 1 or hour > 12 or minute > 59:
        return None

    if period == "AM":
        if hour == 12:
            hour = 0
    else:
        if hour != 12:
            hour += 12

    return datetime(2026, 1, 15, hour, minute)


def extract_end_time(text: str) -> datetime | None:
    """
    Extract an end time from phrases such as:
        until 9 PM
        till 9:30 PM
    """

    pattern = r"\b(?:until|till)\s+(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)\b"

    match = re.search(pattern, text)

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    period = match.group(3).upper()

    if hour < 1 or hour > 12 or minute > 59:
        return None

    if period == "AM":
        if hour == 12:
            hour = 0
    else:
        if hour != 12:
            hour += 12

    return datetime(2026, 1, 15, hour, minute)

def extract_location(text: str) -> str | None:
    """
    Extract a small set of known locations from statement text.

    This is an initial deterministic extractor.
    Later this will be replaced/extended with proper NLP.
    """

    locations = [
        "home",
        "office",
        "school",
        "college",
        "hospital",
        "airport",
        "restaurant",
        "hotel",
    ]

    text_lower = text.lower()

    for location in locations:
        if re.search(rf"\b{re.escape(location)}\b", text_lower):
            return location

    return None


def extract_subject_action(
    text: str,
) -> tuple[str | None, str | None]:
    """
    Extract a basic subject and action from a sentence.

    This is an initial rule-based NLP layer.
    """

    patterns = [
        (r"\b(the person|he|she|they)\s+(left)\b", "left"),
        (r"\b(the person|he|she|they)\s+(arrived)\b", "arrived"),
        (r"\b(the person|he|she|they)\s+(went)\b", "went"),
        (r"\b(the person|he|she|they)\s+(stayed)\b", "stayed"),
        (r"\b(the person|he|she|they)\s+(was)\b", "was"),
        (r"\b(the person|he|she|they)\s+(visited)\b", "visited"),
    ]

    text_lower = text.lower()

    for pattern, action in patterns:
        match = re.search(pattern, text_lower)

        if match:
            subject = match.group(1)
            return subject, action

    return None, None