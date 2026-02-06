import uuid
import joblib
from sentence_transformers import SentenceTransformer

from ml_pipeline.orchestrator import chatbot_pipeline
from ml_pipeline.response_resolver import ResponseResolver
from utils.preprocess import preprocess_text

from session.session_manager import SessionManager
from session.context_extractor import extract_context
from session.memory_resolver import resolve_memory_question

from flow_pipeline.flow_handler import FlowHandler
from flow_pipeline.flow_registry import flow_registry


# ================= LOAD MODELS =================

semantic_model = SentenceTransformer("semantic_model/")
classifier = joblib.load("model/svc_classifier.joblib")
resolver = ResponseResolver("responses/intent_responses.yml")

# ================= SESSION & FLOW =================

session_manager = SessionManager(session_timeout=600)
flow_handler = FlowHandler(session_manager)

session_id = str(uuid.uuid4())

print("\n🤖 CLI Chatbot running (type 'exit' to quit)\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        print("Bot: Goodbye!")
        break

    # ================= SESSION =================
    session = session_manager.get_or_create_session(session_id)

    # ================= DEBUG =================
    if user_input == "/history":
        print("\n--- SESSION HISTORY ---")
        for msg in session_manager.get_history(session_id):
            print(f"[{msg['role'].upper()}] {msg['text']} ({msg.get('source')})")
        print("-----------------------\n")
        continue

    # ================= PASSIVE CONTEXT EXTRACTION =================
    extracted = extract_context(user_input)
    for k, v in extracted.items():
        session["slots"][k] = v

    # ================= MEMORY QUESTIONS =================
    memory_reply = resolve_memory_question(user_input, session)
    if memory_reply:
        print(f"Bot: {memory_reply}")
        session_manager.add_message(session_id, "bot", memory_reply, "MEMORY")
        continue

    # ================= ACTIVE FLOW =================
    if session.get("active_flow"):
        flow_response = flow_handler.handle_response(session_id, user_input)

        if flow_response.get("success"):
            print(f"Bot: {flow_response.get('reply')}")
        else:
            print(f"Bot: {flow_response.get('error')}")

        session_manager.add_message(session_id, "user", user_input)
        session_manager.add_message(session_id, "bot", flow_response.get("reply"), "FLOW")
        continue

    # ================= ORCHESTRATOR =================
    response = chatbot_pipeline(
        query=user_input,
        classifier=classifier,
        semantic_model=semantic_model,
        preprocess_fn=preprocess_text,
        response_resolver=resolver,
        session_id=session_id
    )

    print("\nBot Response:")
    print(f"  reply      : {response['reply']}")
    print(f"  intent     : {response['intent']}")
    print(f"  confidence : {response['confidence']}")
    print(f"  source     : {response['source']}")

    session_manager.add_message(session_id, "user", user_input)
    session_manager.add_message(session_id, "bot", response["reply"], response["source"])

    # ================= START FLOW IF NEEDED =================
    if flow_registry.has_flow(response["intent"]):
        flow_start = flow_handler.start_flow(response["intent"], session_id)

        if flow_start.get("success"):
            session["active_flow"] = response["intent"]
            print("\n🔄 Flow started")
            print(f"Bot: {flow_start['reply']}")
