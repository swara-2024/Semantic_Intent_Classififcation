from ml_pipeline.orchestrator import chatbot_pipeline
from ml_pipeline.response_resolver import ResponseResolver
from utils.preprocess import preprocess_text
import joblib
from sentence_transformers import SentenceTransformer

# === LOAD MODELS ONCE ===
semantic_model = SentenceTransformer("semantic_model/")
classifier = joblib.load("model/svc_classifier.joblib")
resolver = ResponseResolver("responses/intent_responses.yml")

print("Models loaded successfully.")
print("Chatbot is running (type 'exit' to quit)\n")

while True:
    user_query = input("You: ").strip()

    if not user_query:
        print("Bot: Please enter a message.")
        continue

    if user_query.lower() in ["exit", "quit"]:
        print("Bot: Goodbye!")
        break

    try:
        response = chatbot_pipeline(
            query=user_query,
            classifier=classifier,
            semantic_model=semantic_model,
            preprocess_fn=preprocess_text,
            response_resolver=resolver
        )

        print("Bot Response:")
        print(f"  reply            : {response.get('reply')}")
        print(f"  intent           : {response.get('intent')}")
        print(f"  predicted_intent : {response.get('predicted_intent')}")
        print(f"  confidence       : {response.get('confidence')}")
        print(f"  source           : {response.get('source')}")
        print("-" * 50)

    except Exception as e:
        print("Error:", e)
        print("-" * 50)
