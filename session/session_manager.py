# session/session_manager.py

import time

class SessionManager:
    def __init__(self, session_timeout: int = 600):
        self.session_timeout = session_timeout
        self.sessions = {}

    def get_or_create_session(self, session_id: str) -> dict:
        session = self.sessions.get(session_id)

        if not session:
            session = {
                "active_flow": None,
                "pending_flow": None,
                "last_completed_flow": None,   # ✅ KEY
                "current_step": 0,
                "slots": {},
                "last_intent": None,
                "history": [],
                "created_at": time.time(),
                "last_active": time.time()
            }
            self.sessions[session_id] = session
            return session

        if time.time() - session["last_active"] > self.session_timeout:
            self.delete_session(session_id)
            return self.get_or_create_session(session_id)

        return session

    def delete_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def update_intent(self, session_id: str, intent: str | None):
        session = self.sessions.get(session_id)
        if session:
            session["last_intent"] = intent
            session["last_active"] = time.time()

    def add_message(self, session_id: str, role: str, text: str, source: str | None = None):
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

    def get_history(self, session_id: str):
        session = self.sessions.get(session_id)
        return session["history"] if session else []

    def get_session_snapshot(self, session_id: str):
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            "active_flow": session["active_flow"],
            "pending_flow": session["pending_flow"],
            "last_completed_flow": session["last_completed_flow"],
            "current_step": session["current_step"],
            "slots": session["slots"],
            "last_intent": session["last_intent"],
            "history_length": len(session["history"]),
        }
