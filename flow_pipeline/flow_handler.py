# flow_pipeline/flow_handler.py

import time
from flow_pipeline.post_flow_actions import handle_post_flow
from flow_pipeline.flow_registry import flow_registry
from flow_pipeline.flow_loader import validate_flow_structure
from flow_pipeline.validators import SlotValidator
from session.session_manager import SessionManager


class FlowHandler:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def start_flow(self, intent: str, user_id: str) -> dict:
        flow_def = flow_registry.get_flow_for_intent(intent)
        if not flow_def:
            return {"success": False, "error": "No flow found"}

        valid, error = validate_flow_structure(flow_def)
        if not valid:
            return {"success": False, "error": error}

        session = self.session_manager.get_or_create_session(user_id)

        session["active_flow"] = intent
        session["current_step"] = 0
        session.setdefault("slots", {})   #  KEEP existing memory
        session["last_active"] = time.time()

        question = flow_def["steps"][0]["question"]

        return {
            "success": True,
            "completed": False,
            "intent": intent,
            "reply": question
        }

    def handle_response(self, user_id: str, user_response: str) -> dict:
        session = self.session_manager.get_or_create_session(user_id)
        intent = session.get("active_flow")

        if not intent:
            return {"success": False, "error": "No active flow"}

        flow_def = flow_registry.get_flow_for_intent(intent)
        steps = flow_def["steps"]
        step_idx = session["current_step"]
        step_def = steps[step_idx]

        slot = step_def.get("slot")

        is_valid, error = SlotValidator.validate_slot(
            slot, user_response, step_def.get("validation", {})
        )

        if not is_valid:
            return {
                "success": True,
                "completed": False,
                "reply": error or step_def["question"]
            }

        if slot:
            session["slots"][slot] = user_response   # ✅ unified memory

        session["current_step"] += 1

        if session["current_step"] >= len(steps):
            session["active_flow"] = None
            session["last_completed_flow"] = intent
            session["current_step"] = 0

            #  Send email / webhook / CRM
            handle_post_flow(intent, session["slots"])

            return {
                "success": True,
                "completed": True,
                "intent": intent,
                "reply": (
                    "Thank you! We have collected all the information. "
                    "Our team will contact you shortly."
                )
            }

        return {
            "success": True,
            "completed": False,
            "reply": steps[session["current_step"]]["question"]
        }

    def cancel_flow(self, user_id: str):
        session = self.session_manager.get_or_create_session(user_id)

        session["active_flow"] = None
        session["pending_flow"] = None
        session["current_step"] = 0
        # do NOT clear slots

        return {"success": True, "message": "Flow cancelled"}
