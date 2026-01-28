# main.py - CLI Chatbot Tester (Rule → ML → Flow)

from ml_pipeline.orchestrator import chatbot_pipeline
from ml_pipeline.response_resolver import ResponseResolver
from utils.preprocess import preprocess_text
import joblib
from sentence_transformers import SentenceTransformer
import uuid

# -------------------- Load Models --------------------
print("Loading models...")
semantic_model = SentenceTransformer("semantic_model/")
classifier = joblib.load("model/svc_classifier.joblib")
resolver = ResponseResolver("responses/intent_responses.yml")
print("Models loaded.\n")

# -------------------- Session --------------------
session_id = str(uuid.uuid4())

print("🤖 CLI Chatbot is running (type 'exit' to quit)\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ["exit", "quit"]:
        print("Bot: Goodbye 👋")
        break

    # -------------------- Chatbot Pipeline --------------------
    response = chatbot_pipeline(
        query=user_input,
        classifier=classifier,
        semantic_model=semantic_model,
        preprocess_fn=preprocess_text,
        response_resolver=resolver,
        session_id=session_id
    )

    print("\nBot Response:")
    print(f"  reply      : {response.get('reply', '')}")
    print(f"  intent     : {response.get('intent', 'N/A')}")
    print(f"  confidence : {response.get('confidence', 'N/A')}")
    print(f"  source     : {response.get('source', 'FLOW')}")


