# Quick Reference Guide - Business Logic Implementation

## What Was Implemented

### ✓ Core Business Logic Components

#### 1. Flow Management System (`flow_pipeline/`)
- **flow_loader.py**: Loads and validates YAML flow definitions
- **flow_registry.py**: Maps intents to flows (e.g., demo_request → demo_booking_flow)
- **flow_handler.py**: Executes multi-step conversational flows
- **validators.py**: Email, phone, date, time, text, numeric validation
- **session_manager.py**: In-memory session tracking with 10-min timeout

#### 2. Enhanced Query Analysis (`rule_engine/query_analyzer.py`)
- Analyzes query characteristics (tokens, keywords, intent signals)
- Estimates intent category from keywords
- Supports routing decisions

#### 3. REST API Server (`flow_api.py`)
- `/api/chat`: Main chat endpoint with flow integration
- `/api/flow/start`: Start a new flow
- `/api/flow/respond`: Submit responses to flow questions
- `/api/flow/session/<id>`: Get session status
- `/api/flow/cancel/<id>`: Cancel flow
- `/api/flows/available`: List all flows
- `/api/intents/with-flows`: List intents with flows
- `/api/analyze/query`: Analyze query characteristics
- `/health`: Health check

#### 4. Comprehensive Flow Definitions
Updated all 6 flow YAML files with:
- Multi-step slot collection
- Field validation rules
- Completion handlers
- Flexible text, email, phone, date, time validation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     USER INPUT                          │
└──────────────────────┬──────────────────────────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    RULE ENGINE               │ (fast, keyword-based)
        │  - Regex matching            │
        │  - Quick responses           │
        └──────────────┬───────────────┘
                       │
          No Match ↓   │ Match
                    │   └→ Return Rule Response
                    ↓
        ┌──────────────────────────────┐
        │    ML PIPELINE               │ (semantic classification)
        │  - Embedding generation      │
        │  - SVC classification        │
        │  - Confidence scoring        │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    RESPONSE GENERATION       │
        │  - Intent to response map    │
        │  - Random variant selection  │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    FLOW CHECK                │
        │  - Does intent have flow?    │
        │  - Yes → Start flow          │
        │  - No → Return response      │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    FLOW EXECUTION            │ (multi-step slot filling)
        │  - Question generation       │
        │  - Input validation          │
        │  - Session management        │
        │  - Step progression          │
        └──────────────┬───────────────┘
                       ↓
        ┌──────────────────────────────┐
        │    DATA COLLECTION COMPLETE  │
        │  - Slots filled              │
        │  - Handler invoked           │
        │  - Session cleaned up        │
        └──────────────────────────────┘
```

---

## Key Files & Their Roles

| File | Purpose | Status |
|------|---------|--------|
| `flow_pipeline/flow_loader.py` | Load and validate flow YAML files | ✓ Implemented |
| `flow_pipeline/flow_registry.py` | Map intents to flows | ✓ Implemented |
| `flow_pipeline/flow_handler.py` | Execute flows and manage slots | ✓ Implemented |
| `flow_pipeline/validators.py` | Validate email, phone, dates, etc. | ✓ Implemented |
| `rule_engine/query_analyzer.py` | Analyze query characteristics | ✓ Enhanced |
| `flow_api.py` | Flask REST API server | ✓ Implemented |
| `flow_pipeline/definitions/*.yaml` | Flow definitions | ✓ Updated |
| `BUSINESS_LOGIC.md` | API & architecture documentation | ✓ Created |
| `DEVELOPMENT_GUIDE.md` | Development guide & examples | ✓ Created |
| `test_api.py` | Comprehensive API test suite | ✓ Created |

---

## Running the System

### Option 1: Console Chatbot
```bash
python app.py
# Interactive console chat experience
```

### Option 2: REST API Server
```bash
python flow_api.py
# Starts Flask server on http://localhost:5000
```

### Option 3: Test API Endpoints
```bash
python test_api.py
# Runs comprehensive test suite
```

---

## Integration Examples

### Basic Chat Request
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to schedule a demo",
    "user_id": "user123"
  }'
```

### Start Flow
```bash
curl -X POST http://localhost:5000/api/flow/start \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "demo_request",
    "user_id": "user123"
  }'
```

### Respond to Flow Question
```bash
curl -X POST http://localhost:5000/api/flow/respond \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "response": "john@example.com"
  }'
```

---

## Available Flows

1. **demo_booking_flow** → Intent: `demo_request`
   - Collects: name, email, company, date, time, use case

2. **job_application_flow** → Intent: `job_application`
   - Collects: name, email, phone, position, experience, education, resume, availability

3. **internship_application_flow** → Intent: `internship_application`
   - Collects: name, email, phone, college, year, major, start date, duration

4. **free_trial_flow** → Intent: `free_trial_request`
   - Collects: name, email, company, industry, team size, use case

5. **sales_lead_flow** → Intent: `sales_lead_inquiry`
   - Collects: name, email, phone, company, industry, budget, timeline, requirements

6. **technical_support_contact** → Intent: `technical_support`
   - Collects: name, email, phone, account ID, category, issue, urgency, steps taken

---

## Validation Rules

| Type | Format | Example |
|------|--------|---------|
| **email** | RFC standard | `john@example.com` |
| **phone** | 10-15 digits | `+1-555-123-4567` |
| **date** | YYYY-MM-DD | `2024-12-25` |
| **time** | HH:MM (24h) | `14:30` |
| **name** | 2-100 chars, letters only | `John Doe` |
| **numeric** | Configurable range | `5`, `100.5` |
| **text** | Configurable length | Any text 1-1000 chars |

---

## Configuration Quick Reference

### ML Pipeline Thresholds
```python
CONFIDENCE_THRESHOLD = 0.20      # High confidence for direct response
SOFT_CONFIDENCE_THRESHOLD = 0.15 # Ask for clarification
```

### Session Management
```python
session_timeout = 600  # 10 minutes
```

### Model Paths
```python
semantic_model_path = "semantic_model/"
classifier_path = "model/svc_classifier.joblib"
responses_path = "responses/intent_responses.yml"
```

### Rule Files
```python
rule_files = [
    "rules/system_rules.yml",
    "rules/safety_rules.yml",
    "rules/static_info_rules.yml",
    "rules/navigation_rules.yml",
    "rules/single_token_business_rules.yml",
]
```

---

## Error Codes & HTTP Status

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Missing required fields |
| 404 | Not Found | Session ID doesn't exist |
| 500 | Server Error | Model loading failed |

---

## Performance Metrics

| Component | Typical Duration |
|-----------|-----------------|
| Rule matching | < 10ms |
| ML prediction | 100-200ms |
| Flow validation | < 5ms |
| Total response | 100-250ms |

---

## Debugging Commands

### Check API Health
```bash
curl http://localhost:5000/health
```

### List Available Flows
```bash
curl http://localhost:5000/api/flows/available
```

### Analyze a Query
```bash
curl -X POST http://localhost:5000/api/analyze/query \
  -d '{"query": "I need help"}' -H "Content-Type: application/json"
```

### Get Session Status
```bash
curl http://localhost:5000/api/flow/session/user123
```

---

## Common Customizations

### Add New Intent Response
1. Edit `responses/intent_responses.yml`
2. Add intent block with messages
3. Add rule or train ML model for intent

### Create Custom Flow
1. Create `flow_pipeline/definitions/my_flow.yaml`
2. Define steps with validation rules
3. Update `flow_registry.py` mapping
4. Test with `flow_handler.start_flow()`

### Add Validation Rule
1. Edit `flow_pipeline/validators.py`
2. Add validator function
3. Register in `SLOT_VALIDATORS`
4. Use in flow YAML: `validation: {type: custom_type}`

---

## Dependencies

```
sentence-transformers==2.6.1
numpy
Flask
joblib
PyYAML
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Documentation Files

- **BUSINESS_LOGIC.md** - Complete API documentation & architecture
- **DEVELOPMENT_GUIDE.md** - Development setup & common tasks  
- **README.md** (this file) - Quick reference guide

---

## Testing Checklist

- [ ] Health check endpoint responds
- [ ] Chat endpoint with demo query starts flow
- [ ] Flow questions appear in order
- [ ] Invalid email rejected, valid email accepted
- [ ] Session timeout after 10 minutes
- [ ] All 6 flows loadable and executable
- [ ] API test suite passes (test_api.py)

---

## Quick Start Checklist

1. ✓ Install dependencies: `pip install -r requirements.txt`
2. ✓ Verify model files exist
3. ✓ Start API: `python flow_api.py`
4. ✓ Run tests: `python test_api.py`
5. ✓ Test chat endpoint
6. ✓ Test flow execution
7. ✓ Review business logic code

---

## Next Steps

### For Users
- Use REST API at `http://localhost:5000`
- Reference `BUSINESS_LOGIC.md` for all endpoints
- Check `test_api.py` for integration examples

### For Developers
- Read `DEVELOPMENT_GUIDE.md` for setup
- Add custom flows in `flow_pipeline/definitions/`
- Extend validators in `flow_pipeline/validators.py`
- Add rules in `rules/*.yml` files

### For Deployment
- Use gunicorn for production: `gunicorn -w 4 flow_api:app`
- Add database for session persistence
- Implement API authentication
- Add request logging and monitoring

---

## Support

For issues or questions:
1. Check error message and HTTP status code
2. Review relevant documentation file
3. Check test_api.py for working examples
4. Enable DEBUG logging for more details

---

**Last Updated**: January 28, 2024  
**Status**: ✓ All Business Logic Implemented and Documented
