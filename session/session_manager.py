# session/session_manager.py

import time


class SessionManager:
    """
    Handles in-memory session management for chatbot users.

    Each session stores:
    - conversational state (intent / flow later)
    - slot data (future use)
    - full chat history (user + bot messages)
    - timestamps for expiry handling
    """

    def __init__(self, session_timeout: int = 600):
        """
        :param session_timeout: session expiry time in seconds (default 10 min)
        """
        self.session_timeout = session_timeout
        self.sessions = {}

    # SESSION LIFECYCLE
  

    def get_or_create_session(self, session_id: str) -> dict:
        """
        Fetch an existing session or create a new one.
        Automatically expires stale sessions.
        """
        session = self.sessions.get(session_id)

        # Create new session if not exists
        if not session:
            session = {
                "active_flow": None,
                "current_step": 0,
                "slots": {},
                "last_intent": None,
                "history": [],            # ✅ full chat history
                "created_at": time.time(),
                "last_active": time.time()
            }
            self.sessions[session_id] = session
            return session

        # Expiry check
        if time.time() - session["last_active"] > self.session_timeout:
            self.delete_session(session_id)
            return self.get_or_create_session(session_id)

        return session

    def delete_session(self, session_id: str):
        """
        Explicitly delete a session.
        """
        self.sessions.pop(session_id, None)

    # SESSION UPDATES


    def update_intent(self, session_id: str, intent: str | None):
        """
        Update last detected intent for debugging/analytics.
        """
        session = self.sessions.get(session_id)
        if not session:
            return

        session["last_intent"] = intent
        session["last_active"] = time.time()

    def add_message(self, session_id: str, role: str, text: str, source: str | None = None):
        """
        Add a user or bot message to session history.

        :param role: "user" or "bot"
        :param text: message text
        :param source: RULE / ML / LLM (for bot only)
        """
        session = self.sessions.get(session_id)
        if not session:
            return

        session["history"].append({
            "role": role,
            "text": text,
            "source": source,
            "timestamp": time.time()
        })

        session["last_active"] = time.time()

    # HELPERS (DEBUGGING)
 

    def get_history(self, session_id: str):
        """
        Return full conversation history for a session.
        """
        session = self.sessions.get(session_id)
        if not session:
            return []

        return session["history"]

    def get_session_snapshot(self, session_id: str) -> dict | None:
        """
        Safe snapshot of session data (for debugging).
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            "active_flow": session["active_flow"],
            "current_step": session["current_step"],
            "slots": session["slots"],
            "last_intent": session["last_intent"],
            "history_length": len(session["history"]),
            "created_at": session["created_at"],
            "last_active": session["last_active"]
        }
