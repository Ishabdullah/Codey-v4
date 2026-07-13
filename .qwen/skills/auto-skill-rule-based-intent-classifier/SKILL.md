---
name: rule-based-intent-classifier
description: Implement deterministic keyword matching classifier for request intent identification
source: auto-skill
extracted_at: '2026-07-12T16:07:03.089Z'
---

**Approach:**
1. Created `RuleBasedIntentClassifier` inheriting from `BaseClassifier` in `/core/rule_based_intent_classifier.py`.
2. Defined five intent categories (`conversation`, `coding`, `planning`, `memory`, `embedding`) with keyword mappings and alias handling.
3. Implemented deterministic classification using regex keyword matching with confidence scoring based on keyword overlap.
4. Mapped aliases to canonical intent names for flexible matching.
5. Returned `ClassificationResult` with intent, confidence, candidate services, and metadata.

**Why:**
- Provides a deterministic, replaceable classifier without runtime dependencies.
- Maintains strict separation from kernel, decision engine, and model layers.
- Enables future replacement with FunctionGemma or cloud classifier without modifying callers.
- Satisfies architectural requirements for modularity and low coupling.

**How to apply:**
1. Instantiate `RuleBasedIntentClassifier()` and pass requests via `classify(request)`.
2. Use the returned `ClassificationResult.intent` to route logic in downstream components.
3. Adjust keyword lists in the classifier to adapt to new intent categories as needed.
4. No runtime changes required; integrates cleanly with existing request/response flow.

This skill establishes a foundational intent classification layer for Codey-v4 while preserving all existing runtime behavior.