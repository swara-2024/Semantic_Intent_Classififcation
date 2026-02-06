import re

def resolve_memory_question(query: str, session: dict):
    text = query.lower()
    slots = session.get("slots", {})

    if re.search(r"\bwhat is my name\b", text):
        name = slots.get("name")
        return f"Your name is {name.capitalize()} 😊" if name else "I don't know your name yet."

    if re.search(r"\bwhat is my email\b", text):
        email = slots.get("email")
        return f"Your email is {email}" if email else "I don't have your email yet."

    return None
