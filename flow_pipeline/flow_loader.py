# flow_pipeline/flow_loader.py

import yaml
import os
from pathlib import Path

def load_flow_definitions(directory="flow_pipeline/definitions"):
    """
    Loads all flow definitions from YAML files in the given directory.
    
    Returns:
        dict: A dictionary mapping flow_name to flow_definition
    """
    flows = {}
    
    if not os.path.exists(directory):
        print(f"Warning: Flow definitions directory '{directory}' not found")
        return flows
    
    for filename in os.listdir(directory):
        if filename.endswith((".yaml", ".yml")):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r") as f:
                    data = yaml.safe_load(f)
                    if data:
                        # Extract flow name from file (e.g., demo_booking_flow.yaml → demo_booking_flow)
                        flow_name = filename.rsplit(".", 1)[0]
                        flows[flow_name] = data
                        print(f"✓ Loaded flow: {flow_name}")
            except Exception as e:
                print(f"✗ Error loading {filename}: {e}")
    
    return flows


def get_flow_definition(flow_name, flows_cache=None):
    """
    Retrieves a specific flow definition.
    
    Args:
        flow_name: Name of the flow (e.g., 'demo_booking_flow')
        flows_cache: Cached flows dictionary (optional)
    
    Returns:
        dict: Flow definition or None if not found
    """
    if flows_cache is None:
        flows_cache = load_flow_definitions()
    
    return flows_cache.get(flow_name)


def validate_flow_structure(flow_definition):
    """
    Validates that a flow definition has the required structure.
    
    Args:
        flow_definition: Flow configuration dictionary
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(flow_definition, dict):
        return False, "Flow definition must be a dictionary"
    
    if "steps" not in flow_definition:
        return False, "Flow must have 'steps' field"
    
    steps = flow_definition["steps"]
    if not isinstance(steps, list):
        return False, "'steps' must be a list"
    
    if len(steps) == 0:
        return False, "Flow must have at least one step"
    
    # Validate each step
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            return False, f"Step {i} must be a dictionary"
        
        if "slot" not in step:
            return False, f"Step {i} missing 'slot' field"
        
        if "question" not in step:
            return False, f"Step {i} missing 'question' field"
    
    return True, None


# Initialize flows on module load
FLOWS_CACHE = load_flow_definitions()