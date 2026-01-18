def rope_response(
    text,
    intent,
    confidence,
    source,
    predicted_intent=None
):
    return {
        "reply": text,
        "intent": intent,                 # final intent (used by UI)
        "predicted_intent": predicted_intent,  # ML output (debug/audit)
        "confidence": round(confidence, 3),
        "source": source
    }
