import re

NAME_PATTERNS = [
    r"\bmy name is (\w+)\b",
    r"\bi am (\w+)\b",
    r"\bthis is (\w+)\b"
]

EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


def extract_context(text: str) -> dict:
    text = text.lower()
    data = {}

    for pattern in NAME_PATTERNS:
        m = re.search(pattern, text)
        if m:
            data["name"] = m.group(1)
            break

    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        data["email"] = email_match.group(0)

    return data
