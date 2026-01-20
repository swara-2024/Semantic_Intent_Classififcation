# ML Pipeline

that combines:

-   **ML-based intent classification**
-   **Response mapping using YAML** 
-   **Confidence-based routing**
-   **LLM fallback (placeholder)**
-   **Rule-engine (placeholder)**

------------------------------------------------------------------------

##  High-Level Flow

    User Input
       ↓
    Rule Engine (placeholder – always fails)
       ↓
    ML Intent Classification
       ↓
    Confidence Check (≥ 0.20 ?)
       ↓
    Intent → Response Mapping (YAML)
       ↓
    LLM Fallback (if response missing or low confidence)
       ↓
    Final Structured Response

------------------------------------------------------------------------

##  Project Structure



    ├── app.py
    │
    ├── ml_pipeline/
    │   ├── __init__.py
    │   ├── orchestrator.py
    │   ├── ml_engine.py
    │   ├── response_resolver.py
    │   └── rope.py
    │
    ├── placeholders/
    │   ├── __init__.py
    │   ├── rule_engine.py
    │   └── llm_engine.py
    │
    ├── responses/
    │   └── intent_responses.yml
    │
    ├── utils/
    │   ├── __init__.py
    │   └── preprocess.py
    │
    ├── model/
    │   └── svc_classifier.joblib
    │
    ├── semantic_model/
    │   └── (SentenceTransformer model files)
    │
    └── README.md

------------------------------------------------------------------------

##  File-by-File Explanation

### `app.py` --- Entry Point (User Interaction)

-   Loads ML models once per session
-   Accepts user input dynamically (CLI)
-   Prints full structured response including: reply, intent,
    predicted_intent, confidence, source

------------------------------------------------------------------------

### `ml_pipeline/orchestrator.py` --- Core Decision Logic

-   Controls chatbot flow
-   Applies confidence threshold
-   Routes to ML response or LLM fallback

------------------------------------------------------------------------

### `ml_pipeline/ml_engine.py` --- ML Intent Prediction

-   Preprocesses input
-   Generates embeddings
-   Predicts intent + confidence
-   Does **not** generate responses

------------------------------------------------------------------------

### `ml_pipeline/response_resolver.py` --- Intent → Response Mapping

-   Maps ML intent to YAML-defined responses
-   Prevents hallucinated outputs

------------------------------------------------------------------------

### `ml_pipeline/rope.py` --- Response Orchestration

-   Standardizes final response format
-   Ensures UI / API consistency

------------------------------------------------------------------------

### `placeholders/rule_engine.py`

-   Placeholder for rule-based engine
-   Currently always fails (returns None)

------------------------------------------------------------------------

### `placeholders/llm_engine.py`

-   Placeholder for LLM fallback
-   Handles low-confidence or unmapped intents

------------------------------------------------------------------------

### `responses/intent_responses.yml`

-   Stores responses for ML-predicted intents
-   Every ML intent must exist here or be aliased

------------------------------------------------------------------------

### `utils/preprocess.py`

-   Normalizes user input
-   Can be extended for spell correction and cleanup



