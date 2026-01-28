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

print("🤖 Chatbot is running (type 'exit' to quit)")
print("Debug commands: /history , /session\n")

# Single-user CLI → one session
session_id = str(uuid.uuid4())

while True:
    user_query = input("You: ").strip()

    # -------------------------------
    # EXIT
    # -------------------------------
    if user_query.lower() in ["exit", "quit"]:
        print("Bot: Goodbye! 👋")
        break

    # Ensure session exists
    session_manager.get_or_create_session(session_id)

    # -------------------------------
    # DEBUG: SHOW FULL CHAT HISTORY
    # -------------------------------
    if user_query == "/history":
        print("\n--- FULL SESSION HISTORY ---")
        history = session_manager.get_history(session_id)
        if not history:
            print("(no messages yet)")
        else:
            for msg in history:
                role = msg["role"].upper()
                text = msg["text"]
                source = msg.get("source")
                print(f"[{role}] {text} ({source})")
        print("-" * 50)
        continue

    # -------------------------------
    # DEBUG: SHOW SESSION STATE
    # -------------------------------
    if user_query == "/session":
        session = session_manager.sessions.get(session_id)
        print("\n--- SESSION STATE ---")
        for k, v in session.items():
            if k == "history":
                print(f"{k}: {len(v)} messages")
            else:
                print(f"{k}: {v}")
        print("-" * 50)
        continue

    try:
        # -------------------------------
        # STORE USER MESSAGE
        # -------------------------------
        session_manager.add_message(
            session_id,
            role="user",
            text=user_query
        )

        # -------------------------------
        # RUN CHATBOT PIPELINE
        # -------------------------------
        response = chatbot_pipeline(
            query=user_query,
            classifier=classifier,
            semantic_model=semantic_model,
            preprocess_fn=preprocess_text,
            response_resolver=resolver,
            session_id=session_id
        )

        # -------------------------------
        # STORE BOT MESSAGE
        # -------------------------------
        session_manager.add_message(
            session_id,
            role="bot",
            text=response.get("reply"),
            source=response.get("source")
        )

        # -------------------------------
        # PRINT BOT RESPONSE
        # -------------------------------
        print("Bot Response:")
        print(f"  reply            : {response.get('reply')}")
        print(f"  intent           : {response.get('intent')}")
        print(f"  predicted_intent : {response.get('predicted_intent')}")
        print(f"  confidence       : {response.get('confidence')}")
        print(f"  source           : {response.get('source')}")
        print("-" * 50)

    except Exception as e:
        print("❌ Error:", e)
        print("-" * 50)
