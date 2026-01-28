# flow_pipeline/app.py - Flask Web API for Semantic Intent Classification

from flask import Flask, request, jsonify
from flow_pipeline.flow_handler import flow_handler
from flow_pipeline.flow_registry import flow_registry
from ml_pipeline.orchestrator import chatbot_pipeline
from ml_pipeline.response_resolver import ResponseResolver
from utils.preprocess import preprocess_text
from rule_engine.query_analyzer import analyze_query_characteristics, get_query_intent_category
import joblib
from sentence_transformers import SentenceTransformer
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load models once
try:
    semantic_model = SentenceTransformer("semantic_model/")
    classifier = joblib.load("model/svc_classifier.joblib")
    resolver = ResponseResolver("responses/intent_responses.yml")
    logger.info("✓ Models loaded successfully")
except Exception as e:
    logger.error(f"✗ Error loading models: {e}")
    raise


# ==================== API ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint - processes user query and returns response.
    
    Request JSON:
    {
        "query": "string",
        "user_id": "optional string"
    }
    """
    try:
        data = request.get_json()
        
        if not data or "query" not in data:
            return jsonify({"success": False, "error": "Missing 'query' field"}), 400
        
        query = data.get("query", "").strip()
        user_id = data.get("user_id")
        
        if not query:
            return jsonify({"success": False, "error": "Query cannot be empty"}), 400
        
        ml_response = chatbot_pipeline(
            query=query,
            classifier=classifier,
            semantic_model=semantic_model,
            preprocess_fn=preprocess_text,
            response_resolver=resolver
        )
        
        intent = ml_response.get("intent")
        has_flow = flow_registry.has_flow(intent)
        flow_data = None
        
        if has_flow and user_id:
            flow_response = flow_handler.start_flow(intent, user_id)
            if flow_response.get("success"):
                flow_data = {
                    "session_id": flow_response.get("session_id"),
                    "current_step": flow_response.get("current_step"),
                    "total_steps": flow_response.get("total_steps"),
                    "question": flow_response.get("question")
                }
        
        return jsonify({
            "success": True,
            "reply": ml_response.get("reply"),
            "intent": intent,
            "confidence": ml_response.get("confidence"),
            "source": ml_response.get("source"),
            "flow_started": flow_data is not None,
            "flow_data": flow_data
        }), 200
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/flow/start', methods=['POST'])
def start_flow():
    """Starts a new flow for a specific intent."""
    try:
        data = request.get_json()
        
        if not data or "intent" not in data:
            return jsonify({"success": False, "error": "Missing 'intent' field"}), 400
        
        intent = data.get("intent")
        user_id = data.get("user_id", f"user_{hash(intent)}")
        
        response = flow_handler.start_flow(intent, user_id)
        status_code = 200 if response.get("success") else 400
        
        return jsonify(response), status_code
    
    except Exception as e:
        logger.error(f"Error starting flow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/flow/respond', methods=['POST'])
def respond_in_flow():
    """Handles user response in an active flow."""
    try:
        data = request.get_json()
        
        if not data or "session_id" not in data or "response" not in data:
            return jsonify({"success": False, "error": "Missing fields"}), 400
        
        session_id = data.get("session_id")
        user_response = data.get("response", "").strip()
        
        if not user_response:
            return jsonify({"success": False, "error": "Response cannot be empty"}), 400
        
        response = flow_handler.handle_response(session_id, user_response)
        status_code = 200 if response.get("success") else 400
        
        return jsonify(response), status_code
    
    except Exception as e:
        logger.error(f"Error handling flow response: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/flow/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Retrieves current session data."""
    try:
        response = flow_handler.get_session_data(session_id)
        status_code = 200 if response.get("success") else 404
        return jsonify(response), status_code
    
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/flow/cancel/<session_id>', methods=['POST'])
def cancel_flow(session_id):
    """Cancels and cleans up a flow session."""
    try:
        response = flow_handler.cancel_flow(session_id)
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Error cancelling flow: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/flows/available', methods=['GET'])
def get_available_flows():
    """Returns list of all available flows."""
    try:
        flows = flow_registry.get_all_available_flows()
        return jsonify({
            "success": True,
            "flows": list(flows.keys()),
            "count": len(flows)
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving flows: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/intents/with-flows', methods=['GET'])
def get_intents_with_flows():
    """Returns list of intents that have associated flows."""
    try:
        intents = flow_registry.get_all_intents_with_flows()
        return jsonify({
            "success": True,
            "intents": intents,
            "count": len(intents)
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving intents: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/analyze/query', methods=['POST'])
def analyze_query():
    """Analyzes a query and returns characteristics."""
    try:
        data = request.get_json()
        
        if not data or "query" not in data:
            return jsonify({"success": False, "error": "Missing 'query' field"}), 400
        
        query = data.get("query", "").strip()
        analysis = analyze_query_characteristics(query)
        estimated_category = get_query_intent_category(analysis)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "estimated_category": estimated_category
        }), 200
    
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
