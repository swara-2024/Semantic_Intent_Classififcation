# session_manager.py
import time

class SessionManager:
    """
    Handles session-based memory management.
    Each session stores conversational context only for a limited time.
    No database or persistent storage is used.
    """

    def __init__(self, session_timeout=600):
        # session_timeout = 10 minutes (600 seconds)
        self.session_timeout = session_timeout
        self.sessions = {}

    def create_session(self, session_id, intent):
        """
        Creates a new session when a new intent is detected.
        """
        self.sessions[session_id] = {
            "intent": intent,          # active intent / flow
            "state": None,             # current step/state in flow
            "slots": {},               # collected user inputs
            "created_at": time.time(),
            "last_active": time.time()
        }

    def get_session(self, session_id):
        """
        Fetches an existing session if it is still active.
        Automatically expires session after timeout.
        """
        session = self.sessions.get(session_id)

        if not session:
            return None

        # Check session expiry
        if time.time() - session["last_active"] > self.session_timeout:
            self.delete_session(session_id)
            return None

        return session

    def update_session(self, session_id, *, state=None, slot_key=None, slot_value=None):
        """
        Updates session state and/or slot values.
        """
        session = self.sessions.get(session_id)
        if not session:
            return

        if state is not None:
            session["state"] = state

        if slot_key is not None:
            session["slots"][slot_key] = slot_value

        session["last_active"] = time.time()

    def delete_session(self, session_id):
        """
        Deletes session explicitly or on timeout.
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
