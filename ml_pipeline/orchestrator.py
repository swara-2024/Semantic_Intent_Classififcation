from rule_engine.rule_pipeline import RulePipeline
from placeholders.llm_engine import llm_placeholder
from ml_pipeline.ml_engine import ml_predict
from ml_pipeline.rope import rope_response

CONFIDENCE_THRESHOLD = 0.20
SOFT_CONFIDENCE_THRESHOLD = 0.15  

# Initialize rule pipeline once
rule_pipeline = RulePipeline(
    rule_files=[
        "rules/system_rules.yml",
        "rules/safety_rules.yml",
        "rules/static_info_rules.yml",
        "rules/navigation_rules.yml"
    ]
)

def chatbot_pipeline(
    query,
    classifier,
    semantic_model,
    preprocess_fn,
    response_resolver
):
    #  RULE ENGINE
    rule_result = rule_pipeline.run(query)

    if rule_result.get("matched") and not rule_result.get("allow_ml_fallback", True):
        return rope_response(
            text=rule_result["response"],
            intent=rule_result["intent"],
            predicted_intent=None,
            confidence=rule_result["confidence"],
            source="RULE"
        )

    #  ML INTENT PREDICTION
    predicted_intent, confidence = ml_predict(
        query,
        classifier,
        semantic_model,
        preprocess_fn
    )

    #  ML RESPONSE (confident & mapped)
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

    #  SOFT ML FALLBACK (NEW – UX FIX)
    # Handles near-threshold predictions without jumping to LLM
    if predicted_intent and confidence >= SOFT_CONFIDENCE_THRESHOLD:
        return rope_response(
            text="Could you please clarify a bit more so I can help you better?",
            intent="clarification_needed",
            predicted_intent=predicted_intent,
            confidence=confidence,
            source="ML"
        )

    # 5️⃣ LLM FALLBACK (LAST RESORT)
    llm_text = llm_placeholder(query)
    return rope_response(
        text=llm_text,
        intent="unknown",
        predicted_intent=predicted_intent,
        confidence=confidence,
        source="LLM"
    )
