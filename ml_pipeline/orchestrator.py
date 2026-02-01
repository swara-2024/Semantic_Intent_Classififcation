import time

from rule_engine.rule_pipeline import RulePipeline
from placeholders.llm_engine import llm_placeholder
from ml_pipeline.ml_engine import ml_predict
from ml_pipeline.rope import rope_response
from session.session_manager import SessionManager
from flow_pipeline.flow_handler import FlowHandler
from flow_pipeline.flow_registry import flow_registry


# -------------------- THRESHOLDS --------------------
CONFIDENCE_THRESHOLD = 0.20
FLOW_TRIGGER_THRESHOLD = 0.60
FLOW_COOLDOWN_SECONDS = 180


# -------------------- INITIALIZATION --------------------
rule_pipeline = RulePipeline(
    rule_files=[
        "rules/system_rules.yml",
        "rules/safety_rules.yml",
        "rules/static_info_rules.yml",
        "rules/navigation_rules.yml",
        "rules/single_token_business_rules.yml",
    ]
)

session_manager = SessionManager(session_timeout=600)
flow_handler = FlowHandler(session_manager)


# -------------------- HELPER --------------------
def log_turn(session_id, user_text, bot_text, source):
    session_manager.add_message(session_id, "user", user_text)
    session_manager.add_message(session_id, "bot", bot_text, source)


# -------------------- MAIN PIPELINE --------------------
def chatbot_pipeline(
    query,
    classifier,
    semantic_model,
    preprocess_fn,
    response_resolver,
    session_id: str
):
    session = session_manager.get_or_create_session(session_id)

    # -------------------- HISTORY --------------------
    if query.strip().lower() == "/history":
        return rope_response(
            text=session_manager.get_history(session_id),
            intent="history",
            confidence=1.0,
            source="SYSTEM"
        )

    # -------------------- PENDING FLOW CONSENT --------------------
    if session.get("pending_flow"):
        normalized = query.lower().strip()

        if normalized in ["yes", "yeah", "yep", "sure", "ok", "okay"]:
            flow_intent = session["pending_flow"]

            flow_start = flow_handler.start_flow(flow_intent, session_id)
            session["pending_flow"] = None  # defensive clear

            log_turn(session_id, query, flow_start["reply"], "FLOW")

            return rope_response(
                text=flow_start["reply"],
                intent=flow_intent,
                confidence=1.0,
                source="FLOW"
            )

        if normalized in ["no", "nope", "nah"]:
            session["pending_flow"] = None
            msg = "No problem 😊 Let me know how else I can help."
            log_turn(session_id, query, msg, "SYSTEM")

            return rope_response(
                text=msg,
                intent="flow_declined",
                confidence=1.0,
                source="SYSTEM"
            )

        msg = "Please reply with yes or no 😊"
        log_turn(session_id, query, msg, "SYSTEM")

        return rope_response(
            text=msg,
            intent="flow_consent_pending",
            confidence=1.0,
            source="SYSTEM"
        )

    # -------------------- ACTIVE FLOW --------------------
    if session.get("active_flow"):
        flow_resp = flow_handler.handle_response(session_id, query)
        reply = flow_resp.get("reply", "")

        # record completion timestamp to prevent re-trigger loop
        if flow_resp.get("completed"):
            session["flow_completed_at"] = time.time()

        log_turn(session_id, query, reply, "FLOW")

        return rope_response(
            text=reply,
            intent=flow_resp.get("intent"),
            confidence=1.0,
            source="FLOW"
        )

    # -------------------- RULE ENGINE --------------------
    rule = rule_pipeline.run(query)
    if rule.get("matched") and not rule.get("allow_ml_fallback", True):
        log_turn(session_id, query, rule["response"], "RULE")

        return rope_response(
            text=rule["response"],
            intent=rule["intent"],
            confidence=rule["confidence"],
            source="RULE"
        )

    # -------------------- ML INTENT --------------------
    predicted_intent, confidence = ml_predict(
        query,
        classifier,
        semantic_model,
        preprocess_fn
    )
    session_manager.update_intent(session_id, predicted_intent)

    # -------------------- FLOW COOLDOWN CHECK --------------------
    cooldown_ok = True
    if session.get("flow_completed_at"):
        cooldown_ok = (
            time.time() - session["flow_completed_at"]
        ) > FLOW_COOLDOWN_SECONDS

    # -------------------- FLOW CONSENT GATE --------------------
    if (
        confidence >= FLOW_TRIGGER_THRESHOLD
        and cooldown_ok
        and flow_registry.get_flow_for_intent(predicted_intent)
        and session.get("last_completed_flow") != predicted_intent
    ):
        consent_msg = (
            "To help you with this, I’ll need to collect a few details. "
            "Are you okay sharing them? (yes/no)"
        )

        session["pending_flow"] = predicted_intent
        log_turn(session_id, query, consent_msg, "SYSTEM")

        return rope_response(
            text=consent_msg,
            intent="flow_consent",
            confidence=confidence,
            source="SYSTEM"
        )

    # -------------------- NORMAL ML RESPONSE --------------------
    if confidence >= CONFIDENCE_THRESHOLD:
        response_text = response_resolver.resolve(predicted_intent)
        if response_text:
            log_turn(session_id, query, response_text, "ML")

            return rope_response(
                text=response_text,
                intent=predicted_intent,
                confidence=confidence,
                source="ML"
            )

    # -------------------- FALLBACK --------------------
    llm_text = llm_placeholder(query)
    log_turn(session_id, query, llm_text, "LLM")

    return rope_response(
        text=llm_text,
        intent="unknown",
        confidence=confidence,
        source="LLM"
    )
