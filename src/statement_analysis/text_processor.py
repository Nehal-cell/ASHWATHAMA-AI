import re


def clean_statement(text: str) -> str:
    """
    Clean a statement while preserving its meaning.
    """

    if not isinstance(text, str):
        raise TypeError("Statement must be a string.")

    text = text.strip()

    # Replace multiple spaces with a single space
    text = re.sub(r"\s+", " ", text)

    return text


def split_sentences(text: str) -> list[str]:
    """
    Split a statement into individual sentences.
    """

    cleaned_text = clean_statement(text)

    if not cleaned_text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", cleaned_text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]