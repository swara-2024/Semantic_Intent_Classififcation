# app.py - Production API

from flask import Flask, request, jsonify
from ml_pipeline.orchestrator import chatbot_pipeline
from ml_pipeline.response_resolver import ResponseResolver
from utils.preprocess import preprocess_text
import joblib
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging
import uuid

# -------------------- Setup --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# -------------------- Load Models Once --------------------
semantic_model = SentenceTransformer("semantic_model/")
classifier = joblib.load("model/svc_classifier.joblib")
resolver = ResponseResolver("responses/intent_responses.yml")

logger.info("✓ Models loaded successfully")

# -------------------- Health --------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200

# -------------------- Chat Endpoint --------------------
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"success": False, "error": "Missing 'query'"}), 400

        query = data["query"].strip()
        user_id = data.get("user_id")

        if not query:
            return jsonify({"success": False, "error": "Empty query"}), 400

        #  Stable session_id
        session_id = user_id or data.get("session_id") or str(uuid.uuid4())

        #  SINGLE ENTRY POINT
        bot_response = chatbot_pipeline(
            query=query,
            classifier=classifier,
            semantic_model=semantic_model,
            preprocess_fn=preprocess_text,
            response_resolver=resolver,
            session_id=session_id
        )

        return jsonify({
            "success": True,
            "session_id": session_id,
            "reply": bot_response["reply"],
            "intent": bot_response["intent"],
            "confidence": bot_response["confidence"],
            "source": bot_response["source"]
        }), 200

    except Exception as e:
        logger.exception("Chat error")
        return jsonify({"success": False, "error": str(e)}), 500

# -------------------- Flow APIs --------------------
@app.route("/api/flow/respond", methods=["POST"])
def respond_flow():
    data = request.get_json()
    if not data or "session_id" not in data or "response" not in data:
        return jsonify({"success": False, "error": "Missing fields"}), 400

    return jsonify(
        flow_handler.handle_response(
            data["session_id"],
            data["response"]
        )
    ), 200


@app.route("/api/flow/cancel/<session_id>", methods=["POST"])
def cancel_flow(session_id):
    return jsonify(flow_handler.cancel_flow(session_id)), 200


@app.route("/api/flow/session/<session_id>", methods=["GET"])
def get_flow_session(session_id):
    return jsonify(flow_handler.get_session_data(session_id)), 200


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
