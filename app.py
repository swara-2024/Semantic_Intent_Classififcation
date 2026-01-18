import json
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer

# =========================================================
# CONFIG
# =========================================================
INTENTS_PATH = "intents.json"
MODEL_NAME = "all-MiniLM-L6-v2"
FALLBACK_THRESHOLD = 0.20

# =========================================================
# APP INIT
# =========================================================
app = Flask(__name__)

print("🔄 Loading sentence embedding model...")
model = SentenceTransformer(MODEL_NAME)
print("✅ Model loaded")

print("🔄 Loading intents...")
with open(INTENTS_PATH, "r", encoding="utf-8") as f:
    intents = json.load(f)

print("🔄 Computing intent embeddings...")
intent_embeddings = {}

for intent, examples in intents.items():
    if not examples:
        continue

    embeddings = model.encode(
        examples,
        normalize_embeddings=True
    )

    embeddings = np.asarray(embeddings)

    # Ensure final shape is (384,)
    if embeddings.ndim == 1:
        intent_embeddings[intent] = embeddings.reshape(-1)
    else:
        intent_embeddings[intent] = embeddings.mean(axis=0).reshape(-1)

print("✅ Intent embeddings ready")

# =========================================================
# UTILS
# =========================================================
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a).reshape(-1)
    b = np.asarray(b).reshape(-1)
    return float(np.dot(a, b))


def predict_intent(text: str):
    query_embedding = model.encode(
        text,
        normalize_embeddings=True
    )
    query_embedding = np.asarray(query_embedding).reshape(-1)

    best_intent = "fallback"
    best_score = 0.0

    for intent, intent_emb in intent_embeddings.items():
        score = cosine_similarity(query_embedding, intent_emb)
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score < FALLBACK_THRESHOLD:
        return {
            "intent": "fallback",
            "confidence": round(best_score, 4)
        }

    return {
        "intent": best_intent,
        "confidence": round(best_score, 4)
    }

# =========================================================
# ROUTES
# =========================================================
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "text is required"}), 400

    result = predict_intent(text)
    return jsonify(result)

# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
