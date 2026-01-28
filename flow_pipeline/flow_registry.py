# flow_pipeline/flow_registry.py

from flow_pipeline.flow_loader import FLOWS_CACHE

class FlowRegistry:
    """
    Maps intents to their corresponding flow definitions.
    Maintains a registry of which intents trigger which flows.
    """
    
    def __init__(self, flows_cache=None):
        self.flows_cache = flows_cache or FLOWS_CACHE
        # Intent to flow mapping
        self.intent_to_flow = self._build_intent_mapping()
    
    def _build_intent_mapping(self):
        """
        Builds a mapping of intents to flow definitions.
        
        Convention:
        - demo_request → demo_booking_flow
        - job_application → job_application_flow
        - internship_application → internship_application_flow
        - free_trial_request → free_trial_flow
        - sales_lead_inquiry → sales_lead_flow
        - technical_support → technical_support_contact flow
        
        Returns:
            dict: Intent → Flow name mapping
        """
        intent_mapping = {
            "demo_request": "demo_booking_flow",
            "job_application": "job_application_flow",
            "internship_application": "internship_application_flow",
            "free_trial_request": "free_trial_flow",
            "sales_lead_inquiry": "sales_lead_flow",
            "technical_support": "technical_support_contact",
            "sales_contact_request": "sales_lead_flow",
            "partnership_inquiry": "sales_lead_flow",
            "lead_qualification_signal": "sales_lead_flow",
        }
        return intent_mapping
    
    def get_flow_for_intent(self, intent):
        """
        Retrieves the flow definition for a given intent.
        
        Args:
            intent: Intent string (e.g., 'demo_request')
        
        Returns:
            dict: Flow definition or None if intent has no associated flow
        """
        flow_name = self.intent_to_flow.get(intent)
        if flow_name:
            return self.flows_cache.get(flow_name)
        return None
    
    def has_flow(self, intent):
        """
        Checks if an intent has an associated flow.
        
        Args:
            intent: Intent string
        
        Returns:
            bool: True if intent maps to a flow
        """
        return intent in self.intent_to_flow
    
    def get_all_intents_with_flows(self):
        """
        Gets all intents that have associated flows.
        
        Returns:
            list: List of intents with flows
        """
        return list(self.intent_to_flow.keys())
    
    def get_all_available_flows(self):
        """
        Gets all available flow names in the registry.
        
        Returns:
            dict: All loaded flows
        """
        return self.flows_cache


# Initialize global registry
flow_registry = FlowRegistry()
