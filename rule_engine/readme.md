#  Rule Base Engine --- Design & Implementation Guide

This document explains the **Rule Base Engine** used in the chatbot
system.\
The rule engine is the **first layer** in the overall pipeline and is
responsible for **fast, deterministic, and safe intent handling** before
ML and LLM are invoked.

------------------------------------------------------------------------

##  Why a Rule Base Engine?

The rule engine exists to handle intents that are:

-   **Deterministic** (fixed answers)
-   **System-level** (greetings, exits)
-   **Safety-critical** (profanity, abuse)
-   **Navigation-oriented** (contact, complaint routing)

Using rules for these cases: - Reduces latency - Prevents ML
misclassification - Avoids unnecessary LLM calls - Improves user
experience

------------------------------------------------------------------------
##  High-Level Position in the Pipeline

    User Query
       ↓
    Query Analyzer (length & mixed-intent detection)
       ↓
    Rule Base Engine
       ↓
    ML Intent Classifier
       ↓
    LLM Fallback

------------------------------------------------------------------------

##  Folder Structure

    rule_engine/
    ├── rule_pipeline.py
    ├── rule_engine.py
    ├── rule_matcher.py
    ├── rule_loader.py
    ├── query_analyzer.py
    └── __init__.py

    rules/
    ├── system_rules.yml
    ├── safety_rules.yml
    ├── static_info_rules.yml
    └── navigation_rules.yml

------------------------------------------------------------------------

##  Core Design Principles

###  Rules Detect *Form*, Not *Meaning*

-   Short, explicit inputs → Rules
-   Long or descriptive inputs → ML

Example: - `hi` → Rule - `hi I want to explore services` → ML

------------------------------------------------------------------------

###  Strict Matching Only

Rules use: - Word-boundary regex - Token-length limits - Negative
keyword guards

Loose keyword matching is **never used**.

------------------------------------------------------------------------

###  Fail-Fast & Low Latency

-   Regex compiled once at startup
-   Max rule checks per query is bounded
-   Average rule latency: **\< 3 ms**

------------------------------------------------------------------------

##  Query Analyzer (`query_analyzer.py`)

Before rules are evaluated, the query is analyzed.

Rules are **skipped entirely** if: - Token count \> 3 - Query contains
both a business verb and business noun

This prevents greeting hijacks and mixed-intent errors.

------------------------------------------------------------------------

##  Rule Evaluation Flow

1.  Query Analyzer decides whether rules should run
2.  Rules are checked by priority
3.  Each rule applies:
    -   Negative keyword guard
    -   Token-length guard
    -   Regex match
4.  If:
    -   No rule matches → ML
    -   Multiple rules match → ML
    -   One rule matches → return rule response

------------------------------------------------------------------------

##  Rule YAML Schema

All rule files follow the same schema:

``` yaml
- intent: greetings
  category: system
  priority: 1
  confidence: 1.0
  allow_ml_fallback: false
  max_tokens: 2
  match:
    regex:
      - "^hi$"
      - "^hello$"
  response:
    type: static
    messages:
      - "Hello! How can I help you?"
```

------------------------------------------------------------------------

##  Rule Categories

###  System Rules

-   greetings
-   goodbyes
-   gratitude

Handled **only by rules**.

------------------------------------------------------------------------

###  Safety Rules

-   profanity
-   abusive language
-   negative wording

Highest priority.\
ML is never allowed to override.

------------------------------------------------------------------------

###  Static Information Rules

-   business hours
-   office location
-   SLA
-   support contact

Answers are fixed and deterministic.

------------------------------------------------------------------------

###  Navigation Rules

-   contact sales
-   raise complaint
-   help / menu

Rules handle routing first, ML may assist if needed.

------------------------------------------------------------------------

##  ML Fallback Policy

Each rule defines:

``` yaml
allow_ml_fallback: true | false
```

-   `false` → rule response is final
-   `true` → ML may override if confidence is low

------------------------------------------------------------------------

##  Response Ownership

  Layer         Response Source
  ------------- ----------------------------------
  Rule Engine   `rules/*.yml`
  ML            `responses/intent_responses.yml`
  LLM           Generated text

Rule responses **never** use ML response files.

------------------------------------------------------------------------

##  Example Behaviors

  Query               Result
  ------------------- ------------------
  `hi`                Rule → greetings
  `internship`        ML
  `hi internship`     ML
  `business hours`    Rule
  `shut up`           Rule (profanity)
  `pricing details`   ML

------------------------------------------------------------------------

##  Benefits of This Design

-   No intent mismatches
-   Predictable behavior
-   Extremely low latency
-   Easy to extend
-   Enterprise-ready



This rule engine is intentionally strict, boring, and fast --- and
that's exactly why it works.
