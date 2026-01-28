# Development Guide - Semantic Intent Classification System

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Requirements (if needed)
```bash
pip install Flask==2.3.0
```

### 3. Run the Console Chatbot
```bash
python app.py
```

Example interaction:
```
You: I want to schedule a demo
Bot Response:
  reply            : Sure, I can help schedule a demo...
  intent           : demo_request
  predicted_intent : demo_request
  confidence       : 0.85
  source           : ML
```

### 4. Run the Flask API Server
```bash
python flow_api.py
```

The API will be available at `http://localhost:5000`

### 5. Test the API
```bash
python test_api.py
```

---

## Project Structure

```
Semantic_Intent_Classififcation/
├── app.py                              # Console chatbot entry point
├── flow_api.py                         # Flask REST API server
├── test_api.py                         # API test suite
├── requirements.txt                    # Python dependencies
│
├── flow_pipeline/                      # Flow management system
│   ├── __init__.py
│   ├── flow_handler.py                 # Core flow execution (IMPLEMENTED)
│   ├── flow_loader.py                  # Load flow definitions (IMPLEMENTED)
│   ├── flow_registry.py                # Intent → Flow mapping (IMPLEMENTED)
│   ├── validators.py                   # Input validation (IMPLEMENTED)
│   ├── session_manager.py              # Session state management
│   └── definitions/                    # Flow YAML files
│       ├── demo_booking_flow.yaml      # Demo booking flow (UPDATED)
│       ├── job_application_flow.yaml   # Job application flow (UPDATED)
│       ├── internship_application_flow.yaml
│       ├── free_trial_flow.yaml        # Free trial signup (UPDATED)
│       ├── sales_lead_flow.yaml        # Sales lead qualification (UPDATED)
│       └── technical_support_contact.yml
│
├── ml_pipeline/                        # ML intent classification
│   ├── __init__.py
│   ├── ml_engine.py                    # ML prediction
│   ├── orchestrator.py                 # Pipeline orchestration
│   ├── response_resolver.py            # Intent → Response mapping
│   └── rope.py                         # Response formatting
│
├── rule_engine/                        # Rule-based intent matching
│   ├── __init__.py
│   ├── rule_engine.py                  # Rule matching logic
│   ├── rule_loader.py                  # Load rule YAML files
│   ├── rule_matcher.py                 # Pattern matching
│   ├── query_analyzer.py               # Query analysis (ENHANCED)
│   └── rule_pipeline.py                # Rule pipeline orchestration
│
├── rules/                              # Rule definitions
│   ├── system_rules.yml
│   ├── safety_rules.yml
│   ├── static_info_rules.yml
│   ├── navigation_rules.yml
│   └── single_token_business_rules.yml
│
├── ml_pipeline/                        # ML resources
│   └── Readme.md
│
├── model/                              # Trained models
│   ├── logistic_regression_classifier.joblib
│   └── svc_classifier.joblib           # Active classifier
│
├── semantic_model/                     # Sentence embeddings
│   ├── config.json
│   ├── model.safetensors
│   └── ... (other model files)
│
├── responses/                          # Intent response templates
│   └── intent_responses.yml
│
├── placeholders/                       # Mock implementations
│   ├── __init__.py
│   └── llm_engine.py                   # Fallback LLM placeholder
│
├── utils/                              # Utilities
│   ├── __init__.py
│   └── preprocess.py                   # Text preprocessing
│
├── templates/                          # HTML/Web UI
│   └── index.html
│
└── BUSINESS_LOGIC.md                   # This documentation (CREATED)
```

---

## Business Logic Components

### 1. Text Preprocessing (`utils/preprocess.py`)
```python
from utils.preprocess import preprocess_text

text = "How much does your service cost?"
cleaned = preprocess_text(text)
# Returns: "how much does your service cost"
```

### 2. Rule Engine (`rule_engine/`)
- **Fast matching** for keyword-based queries
- **Regex patterns** for flexible matching
- **Confidence scores** and **conflict resolution**
- **Token limits** to prevent long-form input

### 3. ML Pipeline (`ml_pipeline/`)
- **Semantic embeddings** using SentenceTransformer
- **SVC classification** for intent prediction
- **Confidence thresholds** for quality control
- **Response mapping** from intent to response

### 4. Flow System (`flow_pipeline/`)
- **Multi-step conversations** for structured data collection
- **Input validation** for email, phone, date, time, text
- **Session management** with automatic timeout
- **Flexible flow definitions** in YAML

### 5. API Layer (`flow_api.py`)
- **RESTful endpoints** for chat and flows
- **Error handling** with proper HTTP status codes
- **Session tracking** across requests
- **Query analysis** for debugging

---

## Common Development Tasks

### Add a New Intent Response

Edit `responses/intent_responses.yml`:
```yaml
new_intent:
  messages:
    - "First response variant"
    - "Second response variant"
    - "Third response variant"
```

Then train/update classifier or add rule in `rules/`.

---

### Add a New Rule

Edit `rules/single_token_business_rules.yml` or appropriate file:
```yaml
- intent: new_intent
  category: business
  priority: 10
  confidence: 0.95
  allow_ml_fallback: true
  max_tokens: 5
  description: "Description of this rule"
  match:
    regex:
      - "^exact phrase$"
      - "keyword.*pattern"
  response:
    type: static
    messages:
      - "Response message"
```

---

### Create a New Flow

1. Create file: `flow_pipeline/definitions/my_flow.yaml`

```yaml
steps:
  - slot: field_name
    question: "Question to ask user?"
    type: text
    validation:
      type: email  # or: phone, name, date, time, numeric
    required: true

  - slot: another_field
    question: "Another question?"
    type: text
    validation:
      type: text
      min_length: 10
      max_length: 500
    required: false

on_complete: my_handler_function
```

2. Update `flow_pipeline/flow_registry.py`:
```python
def _build_intent_mapping(self):
    intent_mapping = {
        "my_intent": "my_flow",
        ...
    }
    return intent_mapping
```

3. Test:
```python
from flow_pipeline.flow_handler import flow_handler

result = flow_handler.start_flow("my_intent", "user123")
print(result['question'])  # First question from flow
```

---

### Add Custom Validation

Edit `flow_pipeline/validators.py`:

```python
# Add to SlotValidator.SLOT_VALIDATORS
SLOT_VALIDATORS = {
    'custom_type': validate_custom_type,
    ...
}

def validate_custom_type(value):
    """Validate custom type"""
    if your_condition(value):
        return True, None
    return False, "Error message for user"
```

---

### Debug a Query

Use the analysis endpoint:
```bash
curl -X POST http://localhost:5000/api/analyze/query \
  -H "Content-Type: application/json" \
  -d '{"query": "your query here"}'
```

Response shows:
- Token count
- Keywords detected
- Estimated intent category
- Question/command status

---

## Testing

### Unit Tests
```bash
# Test individual components
python -m pytest flow_pipeline/tests/
python -m pytest ml_pipeline/tests/
python -m pytest rule_engine/tests/
```

### Integration Tests
```bash
# Test API endpoints
python test_api.py
```

### Manual Testing
```python
# Test flow handler
from flow_pipeline.flow_handler import flow_handler

# Start flow
result = flow_handler.start_flow("demo_request", "test_user")
print(result['question'])

# Respond
result = flow_handler.handle_response("test_user", "John Doe")
print(result['question'])  # Next question
```

---

## Performance Optimization

### Model Loading
- Models are loaded **once** at startup
- Not loaded per-request (for speed)
- In `app.py` and `flow_api.py`

### Caching
- Flow definitions cached on import
- Rules compiled on load
- Session memory for active sessions

### Scaling
For production:
- Use **gunicorn** for multi-worker setup
- Add **Redis** for distributed sessions
- Use **PostgreSQL** for persistent storage

```bash
# Production server
gunicorn -w 4 -b 0.0.0.0:5000 flow_api:app
```

---

## Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Session State
```bash
curl http://localhost:5000/api/flow/session/user123
```

### Test Rule Matching
```python
from rule_engine.rule_pipeline import rule_pipeline

result = rule_pipeline.run("your test query")
print(result)
```

### Test ML Prediction
```python
from ml_pipeline.ml_engine import ml_predict
from sentence_transformers import SentenceTransformer
from utils.preprocess import preprocess_text
import joblib

model = SentenceTransformer("semantic_model/")
clf = joblib.load("model/svc_classifier.joblib")

intent, conf = ml_predict("test query", clf, model, preprocess_text)
print(f"Intent: {intent}, Confidence: {conf}")
```

---

## Common Issues & Solutions

### Models Not Loading
```
ERROR: FileNotFoundError: No such file 'semantic_model/'
```
**Solution**: Ensure models are in correct directory
```bash
ls semantic_model/
ls model/svc_classifier.joblib
```

### Flow Definition Invalid
```
ERROR: Invalid flow definition: Flow must have 'steps' field
```
**Solution**: Check YAML syntax in `flow_pipeline/definitions/`
```bash
python -c "import yaml; yaml.safe_load(open('demo_booking_flow.yaml'))"
```

### Session Not Found
```
ERROR: Session not found or expired
```
**Solution**: Sessions timeout after 10 minutes. Reduce timeout:
```python
session_manager = SessionManager(session_timeout=1800)  # 30 minutes
```

### Validation Fails Unexpectedly
**Solution**: Check validation rules in `validators.py`
```python
from flow_pipeline.validators import InputValidator

is_valid, msg = InputValidator.validate_email("test@example.com")
print(f"Valid: {is_valid}, Message: {msg}")
```

---

## API Documentation

See `BUSINESS_LOGIC.md` for complete API reference including:
- All endpoints
- Request/response formats
- Error codes
- Integration examples

---

## Contributing

1. **Create a branch** for your feature
2. **Write tests** for new functionality
3. **Update documentation** with changes
4. **Test with** `test_api.py` before submitting
5. **Run linting**: `python -m pylint flow_pipeline/`

---

## Resources

- [Sentence Transformers](https://www.sbert.net/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [YAML Syntax](https://yaml.org/)
- [Regex Patterns](https://regex101.com/)

---

Last Updated: January 28, 2024
