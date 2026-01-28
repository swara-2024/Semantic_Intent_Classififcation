# ml_pipeline/orchestrator.py

from rule_engine.rule_pipeline import RulePipeline
from placeholders.llm_engine import llm_placeholder
from ml_pipeline.ml_engine import ml_predict
from ml_pipeline.rope import rope_response
from session.session_manager import SessionManager

CONFIDENCE_THRESHOLD = 0.20
SOFT_CONFIDENCE_THRESHOLD = 0.15

# Initialize rule pipeline once
rule_pipeline = RulePipeline(
    rule_files=[
        "rules/system_rules.yml",
        "rules/safety_rules.yml",
        "rules/static_info_rules.yml",
        "rules/navigation_rules.yml",
        "rules/single_token_business_rules.yml",
    ]
)

# Initialize session manager once
session_manager = SessionManager(session_timeout=600)


def chatbot_pipeline(
    query,
    classifier,
    semantic_model,
    preprocess_fn,
    response_resolver,
    session_id: str
):
    """
    Chatbot orchestration with session awareness (NO FLOW LOGIC).
    """

    # Get or create session
    session = session_manager.get_or_create_session(session_id)

    # RULE ENGINE (highest priority)
    rule_result = rule_pipeline.run(query)

    if rule_result.get("matched") and not rule_result.get("allow_ml_fallback", True):
        session_manager.update_intent(session_id, rule_result["intent"])

        return rope_response(
            text=rule_result["response"],
            intent=rule_result["intent"],
            predicted_intent=None,
            confidence=rule_result["confidence"],
            source="RULE"
        )

    # ML INTENT PREDICTION
    predicted_intent, confidence = ml_predict(
        query,
        classifier,
        semantic_model,
        preprocess_fn
    )

    # Store last ML signal in session (for debugging / analytics)
    session_manager.update_intent(session_id, predicted_intent)

    # ML RESPONSE (confident & mapped)
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

    # SOFT ML FALLBACK (clarification instead of LLM)
    if predicted_intent and confidence >= SOFT_CONFIDENCE_THRESHOLD:
        return rope_response(
            text="Could you please clarify a bit more so I can help you better?",
            intent="clarification_needed",
            predicted_intent=predicted_intent,
            confidence=confidence,
            source="ML"
        )

    # LLM FALLBACK (last resort)
    llm_text = llm_placeholder(query)
    return rope_response(
        text=llm_text,
        intent="unknown",
        predicted_intent=predicted_intent,
        confidence=confidence,
        source="LLM"
    )
