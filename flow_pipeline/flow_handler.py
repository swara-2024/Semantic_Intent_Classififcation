# flow_pipeline/flow_handler.py

from flow_pipeline.flow_registry import flow_registry
from flow_pipeline.flow_loader import validate_flow_structure
from flow_pipeline.validators import SlotValidator
from flow_pipeline.session_manager import SessionManager


class FlowHandler:
    """
    Executes flow logic including:
    - Slot filling
    - Step transitions
    - Validation
    - Flow completion
    """
    
    def __init__(self):
        self.session_manager = SessionManager(session_timeout=600)  # 10 minutes
    
    def start_flow(self, intent, user_id=None):
        """
        Initiates a new flow for a given intent.
        
        Args:
            intent: Intent that triggered the flow
            user_id: Optional user identifier for session tracking
        
        Returns:
            dict: Flow initialization response with first question
        """
        if user_id is None:
            user_id = f"user_{hash(intent)}"
        
        # Get the flow definition
        flow_def = flow_registry.get_flow_for_intent(intent)
        
        if not flow_def:
            return {
                "success": False,
                "error": f"No flow found for intent: {intent}",
                "question": None
            }
        
        # Validate flow structure
        is_valid, error = validate_flow_structure(flow_def)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid flow definition: {error}",
                "question": None
            }
        
        # Create session
        self.session_manager.create_session(user_id, intent)
        
        # Get first step
        first_step = flow_def["steps"][0]
        first_question = first_step["question"]
        
        # Update session with first step
        self.session_manager.update_session(user_id, state=0)
        
        return {
            "success": True,
            "intent": intent,
            "session_id": user_id,
            "current_step": 0,
            "total_steps": len(flow_def["steps"]),
            "question": first_question
        }
    
    def handle_response(self, user_id, user_response):
        """
        Handles user's response to a flow question.
        
        Args:
            user_id: User's session ID
            user_response: User's text response
        
        Returns:
            dict: Response with next question or flow completion status
        """
        # Get session
        session = self.session_manager.get_session(user_id)
        
        if not session:
            return {
                "success": False,
                "error": "Session not found or expired",
                "completed": False
            }
        
        intent = session["intent"]
        current_step = session["state"]
        
        # Get flow definition
        flow_def = flow_registry.get_flow_for_intent(intent)
        
        if not flow_def:
            return {
                "success": False,
                "error": f"Flow not found for intent: {intent}",
                "completed": False
            }
        
        steps = flow_def["steps"]
        
        # Validate current step exists
        if current_step >= len(steps):
            return {
                "success": False,
                "error": "Flow step out of range",
                "completed": False
            }
        
        current_step_def = steps[current_step]
        slot_name = current_step_def["slot"]
        
        # Validate and save user response
        is_valid, error_msg = SlotValidator.validate_slot(
            slot_name,
            user_response,
            current_step_def.get("validation", {})
        )
        
        if not is_valid:
            return {
                "success": False,
                "error": error_msg or "Invalid response. Please try again.",
                "question": current_step_def["question"],  # Repeat the question
                "completed": False
            }
        
        # Store the validated response
        self.session_manager.update_session(
            user_id,
            slot_key=slot_name,
            slot_value=user_response
        )
        
        # Check if more steps
        next_step_index = current_step + 1
        
        if next_step_index < len(steps):
            # Move to next step
            self.session_manager.update_session(user_id, state=next_step_index)
            next_question = steps[next_step_index]["question"]
            
            return {
                "success": True,
                "current_step": next_step_index,
                "total_steps": len(steps),
                "question": next_question,
                "completed": False
            }
        else:
            # Flow completed
            collected_slots = session["slots"]
            completion_action = flow_def.get("on_complete", "handle_completion")
            
            return {
                "success": True,
                "completed": True,
                "intent": intent,
                "collected_data": collected_slots,
                "action": completion_action,
                "message": "Thank you! We have collected all the information. Our team will contact you shortly."
            }
    
    def get_session_data(self, user_id):
        """
        Retrieves current session data.
        
        Args:
            user_id: User's session ID
        
        Returns:
            dict: Session data or error
        """
        session = self.session_manager.get_session(user_id)
        
        if not session:
            return {
                "success": False,
                "error": "Session not found or expired"
            }
        
        flow_def = flow_registry.get_flow_for_intent(session["intent"])
        
        return {
            "success": True,
            "session_id": user_id,
            "intent": session["intent"],
            "current_step": session["state"],
            "total_steps": len(flow_def["steps"]) if flow_def else 0,
            "collected_slots": session["slots"],
            "created_at": session["created_at"],
            "last_active": session["last_active"]
        }
    
    def cancel_flow(self, user_id):
        """
        Cancels and cleans up a flow session.
        
        Args:
            user_id: User's session ID
        
        Returns:
            dict: Confirmation of cancellation
        """
        self.session_manager.delete_session(user_id)
        
        return {
            "success": True,
            "message": "Flow session cancelled successfully"
        }


# Initialize global flow handler
flow_handler = FlowHandler()
