# Semantic Intent Classification - Business Logic & API Documentation

## Overview

This document describes the complete business logic implementation for the Semantic Intent Classification system. The project includes:

1. **ML Pipeline**: Intent classification using semantic models and ML classifiers
2. **Rule Engine**: Keyword-based rules for quick intent resolution
3. **Flow Management**: Multi-step conversational flows for collecting structured information
4. **API Layer**: REST endpoints for integration

---

## Architecture

### High-Level Flow

```
User Input
    ↓
Rule Engine (fast matching)
    ↓ (no match)
ML Pipeline (semantic classification)
    ↓
Response Generation & Flow Check
    ↓
If intent has flow → Start Flow
    ↓
Flow Handler (slot filling)
    ↓
Collect data and complete
```

---

## Core Components

### 1. Rule Engine (`rule_engine/`)

Processes queries using regex-based rules for quick, deterministic responses.

**Key Files:**
- `rule_engine.py`: Main rule processing engine
- `rule_loader.py`: Loads YAML rule files
- `rule_matcher.py`: Matches queries against rules
- `query_analyzer.py`: Analyzes query characteristics

**Features:**
- Token count validation
- Negative keyword guards
- Regex pattern matching
- Priority-based rule ordering

**Rules Configuration:**
Located in `rules/` directory:
- `system_rules.yml`: System-level responses
- `safety_rules.yml`: Safety and compliance rules
- `static_info_rules.yml`: Static information responses
- `navigation_rules.yml`: Navigation and menu rules
- `single_token_business_rules.yml`: Single-word intents

---

### 2. ML Pipeline (`ml_pipeline/`)

Semantic intent classification using sentence transformers and SVM classifier.

**Key Files:**
- `ml_engine.py`: ML prediction logic
- `orchestrator.py`: Main pipeline orchestration
- `response_resolver.py`: Maps intents to responses
- `rope.py`: Response formatting

**Thresholds:**
- `CONFIDENCE_THRESHOLD = 0.20`: High-confidence predictions
- `SOFT_CONFIDENCE_THRESHOLD = 0.15`: Ask for clarification

**Pipeline Logic:**
1. Text preprocessing (lowercase, remove numbers/punctuation)
2. Semantic embedding (SentenceTransformer)
3. Intent prediction (SVC classifier)
4. Confidence scoring
5. Response generation

---

### 3. Flow Pipeline (`flow_pipeline/`)

Multi-step conversational flows for structured data collection.

**Key Files:**
- `flow_handler.py`: Main flow execution logic
- `flow_loader.py`: Loads flow definitions
- `flow_registry.py`: Maps intents to flows
- `validators.py`: Input validation
- `session_manager.py`: Session state management

**Available Flows:**
1. **demo_booking_flow**: Book a product demo
   - Collects: name, email, company, date, time, use case
   
2. **job_application_flow**: Job application submission
   - Collects: name, email, phone, position, experience, education, resume, availability
   
3. **internship_application_flow**: Internship application
   - Collects: name, email, phone, college, year, major, start date, duration
   
4. **free_trial_flow**: Free trial signup
   - Collects: name, email, company, industry, team size, use case
   
5. **sales_lead_flow**: Sales lead qualification
   - Collects: name, email, phone, company, industry, budget, timeline, requirements
   
6. **technical_support_contact**: Support ticket creation
   - Collects: name, email, phone, account ID, category, issue, urgency, steps taken

**Input Validation:**
- Email validation
- Phone number validation (10-15 digits)
- Date validation (YYYY-MM-DD)
- Time validation (HH:MM)
- Text length limits
- Numeric ranges
- Yes/No responses

**Session Management:**
- 10-minute session timeout
- In-memory storage (no database)
- Automatic cleanup on expiry
- Track collected slots

---

## REST API Endpoints

### Base URL
```
http://localhost:5000
```

### 1. Chat Endpoint
**POST** `/api/chat`

Main endpoint for processing user queries.

**Request:**
```json
{
    "query": "I want to schedule a demo",
    "user_id": "user123"  // optional
}
```

**Response:**
```json
{
    "success": true,
    "reply": "Sure, I can help schedule a demo...",
    "intent": "demo_request",
    "confidence": 0.85,
    "source": "ML",
    "flow_started": true,
    "flow_data": {
        "session_id": "user123",
        "current_step": 0,
        "total_steps": 6,
        "question": "May I have your name?"
    }
}
```

---

### 2. Flow Management

#### Start Flow
**POST** `/api/flow/start`

Manually start a flow for a specific intent.

**Request:**
```json
{
    "intent": "demo_request",
    "user_id": "user123"
}
```

**Response:**
```json
{
    "success": true,
    "intent": "demo_request",
    "session_id": "user123",
    "current_step": 0,
    "total_steps": 6,
    "question": "May I have your name?"
}
```

---

#### Respond in Flow
**POST** `/api/flow/respond`

Submit a response to a flow question.

**Request:**
```json
{
    "session_id": "user123",
    "response": "John Doe"
}
```

**Response (if more steps):**
```json
{
    "success": true,
    "current_step": 1,
    "total_steps": 6,
    "question": "Please share your email address.",
    "completed": false
}
```

**Response (if completed):**
```json
{
    "success": true,
    "completed": true,
    "intent": "demo_request",
    "collected_data": {
        "name": "John Doe",
        "email": "john@example.com",
        ...
    },
    "action": "schedule_demo",
    "message": "Thank you! We have collected all the information..."
}
```

---

#### Get Session Data
**GET** `/api/flow/session/<session_id>`

Retrieve current session information.

**Response:**
```json
{
    "success": true,
    "session_id": "user123",
    "intent": "demo_request",
    "current_step": 2,
    "total_steps": 6,
    "collected_slots": {
        "name": "John Doe",
        "email": "john@example.com"
    },
    "created_at": 1234567890.0,
    "last_active": 1234567945.0
}
```

---

#### Cancel Flow
**POST** `/api/flow/cancel/<session_id>`

Cancel and cleanup a flow session.

**Response:**
```json
{
    "success": true,
    "message": "Flow session cancelled successfully"
}
```

---

### 3. Flow Information

#### Get Available Flows
**GET** `/api/flows/available`

List all available flows.

**Response:**
```json
{
    "success": true,
    "flows": [
        "demo_booking_flow",
        "job_application_flow",
        "internship_application_flow",
        "free_trial_flow",
        "sales_lead_flow",
        "technical_support_contact"
    ],
    "count": 6
}
```

---

#### Get Intents with Flows
**GET** `/api/intents/with-flows`

List intents that trigger flows.

**Response:**
```json
{
    "success": true,
    "intents": [
        "demo_request",
        "job_application",
        "internship_application",
        "free_trial_request",
        "sales_lead_inquiry",
        "technical_support"
    ],
    "count": 6
}
```

---

### 4. Query Analysis

#### Analyze Query
**POST** `/api/analyze/query`

Analyze a query and get characteristics.

**Request:**
```json
{
    "query": "I need a demo of your platform"
}
```

**Response:**
```json
{
    "success": true,
    "analysis": {
        "original_query": "I need a demo of your platform",
        "token_count": 6,
        "char_count": 33,
        "is_question": false,
        "is_command": false,
        "is_affirmation": false,
        "is_negation": false,
        "has_pricing_keyword": false,
        "has_demo_keyword": true,
        "has_support_keyword": false,
        "has_contact_keyword": false,
        "has_trial_keyword": false
    },
    "estimated_category": "demo_request"
}
```

---

### 5. Health Check

#### Health
**GET** `/health`

Check API health status.

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-28T10:30:45.123456"
}
```

---

## Error Handling

All endpoints return error responses in this format:

```json
{
    "success": false,
    "error": "Description of the error"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad request (missing/invalid parameters)
- `404`: Not found
- `500`: Server error

---

## Business Logic Examples

### Example 1: Simple Chat → Flow
```
User: "I want to schedule a demo"
  ↓
Rule Engine: No match
  ↓
ML Pipeline: "demo_request" (confidence: 0.85)
  ↓
Response: "Sure, I can help schedule a demo..."
  ↓
Check Registry: demo_request → demo_booking_flow
  ↓
Start Flow: Question 1 - "May I have your name?"
```

### Example 2: Multi-step Flow Collection
```
Question 1: "May I have your name?"
User: "John Doe"
  ↓
Validate: ✓ Valid name
  ↓
Save: name = "John Doe"
  ↓
Question 2: "Please share your email address."
User: "invalid-email"
  ↓
Validate: ✗ Invalid email format
  ↓
Repeat Question 2: "Please share your email address."
User: "john@example.com"
  ↓
Validate: ✓ Valid email
  ↓
Save: email = "john@example.com"
  ↓
Continue to next question...
```

### Example 3: Confidence-based Routing
```
Query: "help"
  ↓
ML Pipeline: predicted_intent = "unknown", confidence = 0.12
  ↓
Check thresholds:
  - confidence (0.12) < CONFIDENCE_THRESHOLD (0.20) ✓
  - confidence (0.12) >= SOFT_CONFIDENCE_THRESHOLD (0.15) ✓
  ↓
Ask for clarification: "Could you please clarify..."
```

---

## Validation Rules

### Email Validation
Pattern: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

### Phone Validation
- 10-15 digits (after removing separators)
- Supports: spaces, hyphens, parentheses

### Date Validation
- Format: `YYYY-MM-DD`
- Example: `2024-12-25`

### Time Validation
- Format: `HH:MM` (24-hour)
- Example: `14:30`

### Name Validation
- 2-100 characters
- Allows: letters, spaces, hyphens, apostrophes

### Text Length
- Configurable min/max length
- Default: 1-1000 characters

---

## Configuration

### Model Paths
- Semantic Model: `semantic_model/`
- SVC Classifier: `model/svc_classifier.joblib`
- Response Mappings: `responses/intent_responses.yml`

### Rule Files
- Location: `rules/`
- Format: YAML
- Auto-loaded on startup

### Flow Definitions
- Location: `flow_pipeline/definitions/`
- Format: YAML
- Auto-loaded on module import

### Session Management
- Timeout: 600 seconds (10 minutes)
- Storage: In-memory (Python dict)
- No persistence across restarts

---

## Integration Guide

### 1. Start the API Server
```bash
export FLASK_APP=flow_api.py
flask run --host=0.0.0.0 --port=5000
```

### 2. Basic Chat Integration
```python
import requests

response = requests.post('http://localhost:5000/api/chat', json={
    'query': 'I want to schedule a demo',
    'user_id': 'user123'
})

result = response.json()
if result['flow_started']:
    print(f"Flow started: {result['flow_data']['question']}")
```

### 3. Flow Interaction Loop
```python
import requests

# Start flow
response = requests.post('http://localhost:5000/api/flow/start', json={
    'intent': 'demo_request',
    'user_id': 'user123'
})

session = response.json()
session_id = session['session_id']

# Collect responses
while True:
    user_input = input(f"{session['question']}\n> ")
    
    response = requests.post('http://localhost:5000/api/flow/respond', json={
        'session_id': session_id,
        'response': user_input
    })
    
    result = response.json()
    
    if result['completed']:
        print("Flow completed!")
        print(f"Collected data: {result['collected_data']}")
        break
    elif result['success']:
        print(result['question'])
    else:
        print(f"Error: {result['error']}")
```

---

## Performance Considerations

1. **Model Loading**: Models are loaded once on startup (not per-request)
2. **Session Management**: In-memory storage suitable for < 10k concurrent sessions
3. **Rule Engine**: O(n) where n = number of rules (typically < 50)
4. **ML Pipeline**: ~100-200ms per prediction (depends on model)

---

## Future Enhancements

1. **Database Integration**: Store sessions and completed flows
2. **Advanced Analytics**: Track intent accuracy, flow completion rates
3. **Multi-language Support**: Extend validation and flow handling
4. **Custom Rules**: API to add/modify rules at runtime
5. **Flow Branching**: Conditional flow steps based on responses
6. **Integration Webhooks**: POST completed flows to external systems
7. **Rate Limiting**: API request throttling
8. **Authentication**: API key/JWT authentication

---

## Troubleshooting

### Model Loading Fails
- Check model paths in configuration
- Verify `semantic_model/` directory exists
- Ensure `model/svc_classifier.joblib` is present

### Flow Definition Errors
- Validate YAML syntax in `flow_pipeline/definitions/`
- Check required fields: `steps`, `on_complete`
- Verify slot validation rules

### Session Timeouts
- Sessions expire after 10 minutes of inactivity
- Increase timeout in `SessionManager.__init__(session_timeout=xxx)`

### Validation Failures
- Check error message for specific failure reason
- Review validation rules in `flow_pipeline/validators.py`
- Test with valid sample data

---

## License & Contact

For questions or support, please contact the development team.

Last Updated: January 28, 2024
