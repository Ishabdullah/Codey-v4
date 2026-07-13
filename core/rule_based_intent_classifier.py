"""
Rule-based intent classifier for request classification.

This classifier uses deterministic keyword matching to identify the most likely
intent from a request prompt. It supports five initial intents:
conversation, coding, planning, memory, embedding

The implementation is intentionally simple and replaceable.
"""

import re
from typing import List, Dict, Any
from .base_classifier import BaseClassifier, ClassificationResult
from .request import Request


class RuleBasedIntentClassifier(BaseClassifier):
    """Concrete implementation of BaseClassifier using keyword matching."""

    def __init__(self):
        # Define intent categories and their associated keywords
        self.intent_keywords: Dict[str, List[str]] = {
            "conversation": [
                "chat", "talk", "converse", "discuss", "conversation", 
                "dialogue", "discussion", "chatbot", "talking", "speak"
            ],
            "coding": [
                "code", "program", "develop", "implement", "function", 
                "class", "method", "variable", "debug", "algorithm", 
                "python", "java", "javascript", "c++", "go", "rust", 
                "typescript", "function", "method", "variable", "debug"
            ],
            "planning": [
                "plan", "schedule", "organize", "strategy", "roadmap", 
                "plan", "goal", "objective", "task", "workflow", "design",
                "blueprint", "schematic", "outline", "prioritize"
            ],
            "memory": [
                "remember", "note", "memory", "store", "recall", "retain", 
                "save", "fact", "remembering", "note-taking", "recording"
            ],
            "embedding": [
                "embed", "vector", "similarity", "semantic", "meaning", 
                "representation", "encode", "decode", "similarity", 
                "distance", "cosine", "embedding", "semantic"
            ]
        }

        # Map for intent aliases to canonical names
        self.intent_aliases: Dict[str, str] = {
            "chatting": "conversation",
            "talking": "conversation",
            "discussing": "conversation",
            "coding": "coding",
            "programming": "coding",
            "developing": "coding",
            "planning": "planning",
            "scheduling": "planning",
            "organizing": "planning",
            "memorizing": "memory",
            "remembering": "memory",
            "storing": "memory",
            "embedding": "embedding",
            "vectorizing": "embedding"
        }

    @property
    def name(self) -> str:
        """Stable identifier for this classifier."""
        return "rule_based_intent_classifier"

    def classify(self, request: Request) -> ClassificationResult:
        """Classify the request prompt into one of the supported intents."""
        # Normalize the prompt for case-insensitive matching
        prompt_lower = request.prompt.lower()
        
        # Check for intent aliases first
        matched_intent = None
        for alias, canonical_intent in self.intent_aliases.items():
            if re.search(rf'\b{re.escape(alias)}\b', prompt_lower):
                matched_intent = canonical_intent
                break
        
        # If no alias matched, check the main keywords
        if not matched_intent:
            for intent, keywords in self.intent_keywords.items():
                for keyword in keywords:
                    if re.search(rf'\b{re.escape(keyword)}\b', prompt_lower):
                        matched_intent = intent
                        break
                if matched_intent:
                    break
        
        # Default to 'conversation' if no intent is clearly identified
        if not matched_intent:
            matched_intent = "conversation"

        # Calculate confidence based on keyword matches
        confidence = 0.0
        matched_keywords = []
        
        # Count matches for the selected intent
        for keyword in self.intent_keywords[matched_intent]:
            if re.search(rf'\b{re.escape(keyword)}\b', prompt_lower):
                matched_keywords.append(keyword)
                confidence += 0.1  # Each matched keyword contributes 0.1 to confidence
        
        # Cap confidence at 1.0
        confidence = min(confidence, 1.0)
        
        # Determine candidate services based on intent
        candidate_services = []
        if matched_intent == "coding":
            candidate_services = ["coding-service", "code-executor"]
        elif matched_intent == "planning":
            candidate_services = ["planning-service", "task-manager"]
        elif matched_intent == "memory":
            candidate_services = ["memory-service"]
        elif matched_intent == "embedding":
            candidate_services = ["embedding-service"]
        # conversation and memory don't need specific services

        return ClassificationResult(
            intent=matched_intent,
            confidence=confidence,
            candidate_services=candidate_services,
            metadata={
                "matched_keywords": matched_keywords,
                "keyword_count": len(matched_keywords)
            }
        )