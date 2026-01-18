from placeholders.rule_engine import rule_engine_placeholder
from placeholders.llm_engine import llm_placeholder
from ml_pipeline.ml_engine import ml_predict
from ml_pipeline.rope import rope_response

CONFIDENCE_THRESHOLD = 0.20

def chatbot_pipeline(
    query,
    classifier,
    semantic_model,
    preprocess_fn,
    response_resolver
):
    # 1️⃣ Rule base placeholder
    rule_result = rule_engine_placeholder(query)
    if rule_result:
        return rope_response(
            text=rule_result,
            intent="system_intent",
            predicted_intent=None,
            confidence=1.0,
            source="RULE"
        )

    # 2️⃣ ML prediction
    predicted_intent, confidence = ml_predict(
        query,
        classifier,
        semantic_model,
        preprocess_fn
    )

    # 3️⃣ ML response if confident and mapped
    if confidence >= CONFIDENCE_THRESHOLD:
        response_text = response_resolver.resolve(predicted_intent)

        if response_text:
            return rope_response(
                text=response_text,
                intent=predicted_intent,
                predicted_intent=predicted_intent,
                confidence=confidence,
                source="ML"
            )

    # 4️⃣ LLM fallback (BUT KEEP ML PREDICTION)
    llm_text = llm_placeholder(query)
    return rope_response(
        text=llm_text,
        intent="unknown",                  # final intent unknown
        predicted_intent=predicted_intent, # ✅ ML result preserved
        confidence=confidence,
        source="LLM"
    )
