# app.py
from session_manager import SessionManager
import uuid

# Initialize session manager with 10 min timeout
session_manager = SessionManager(session_timeout=600)

def detect_intent(user_message):
    """
    Very simple intent detection placeholder.
    Real logic can be rule-based or ML-based.
    """
    if "job" in user_message.lower():
        return "job_application"
    if "demo" in user_message.lower():
        return "demo_booking"
    if "issue" in user_message.lower():
        return "support_ticket"
    return None


def handle_user_message(user_message, session_id=None):
    """
    Core request handler that shows how session is used.
    """

    # Generate session_id for new user
    if not session_id:
        session_id = str(uuid.uuid4())

    # Fetch session
    session = session_manager.get_session(session_id)

    # If no session → new conversation
    if not session:
        intent = detect_intent(user_message)
        if not intent:
            return "Sorry, I didn’t understand that.", session_id

        session_manager.create_session(session_id, intent)
        session_manager.update_session(session_id, state="entry")

        return f"Starting {intent} flow.", session_id

    # Existing session → continue flow
    session_manager.update_session(session_id)

    return "Continuing existing session flow.", session_id
