from ml_pipeline.orchestrator import chatbot_pipeline
from ml_pipeline.response_resolver import ResponseResolver
from utils.preprocess import preprocess_text
from session.session_manager import SessionManager
import joblib
from sentence_transformers import SentenceTransformer
import uuid

# === LOAD MODELS ===
semantic_model = SentenceTransformer("semantic_model/")
classifier = joblib.load("model/svc_classifier.joblib")
resolver = ResponseResolver("responses/intent_responses.yml")

# === SESSION MANAGER ===
session_manager = SessionManager(session_timeout=600)

print("Chatbot is running (type 'exit' to quit)\n")

# Single-user CLI → one session_id
session_id = str(uuid.uuid4())

while True:
    user_query = input("You: ").strip()

    if user_query.lower() in ["exit", "quit"]:
        print("Bot: Goodbye!")
        break

    try:
        # Ensure session exists
        session_manager.get_or_create_session(session_id)

        # Store USER message
        session_manager.add_message(
            session_id,
            role="user",
            text=user_query
        )

        # Run chatbot pipeline
        response = chatbot_pipeline(
            query=user_query,
            classifier=classifier,
            semantic_model=semantic_model,
            preprocess_fn=preprocess_text,
            response_resolver=resolver,
            session_id=session_id
        )

        #  Store BOT message
        session_manager.add_message(
            session_id,
            role="bot",
            text=response.get("reply"),
            source=response.get("source")
        )

        # Print response
        print("Bot Response:")
        print(f"  reply            : {response.get('reply')}")
        print(f"  intent           : {response.get('intent')}")
        print(f"  predicted_intent : {response.get('predicted_intent')}")
        print(f"  confidence       : {response.get('confidence')}")
        print(f"  source           : {response.get('source')}")
        print("-" * 50)

        # OPTIONAL: print session history for debugging
        # print("DEBUG HISTORY:", session_manager.get_history(session_id))

    except Exception as e:
        print(" Error:", e)
        print("-" * 50)
