#!/usr/bin/env python3

# ModelDescriptor Contract
# Phase 1 Implementation
# Infrastructure-only model metadata

from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ModelInfo:
    """Model identity and basic properties (preserved for backward compatibility)."""
    name: str        # Model identifier (e.g., "primary")
    version: str     # Semantic version string (e.g., "2.1.0")
    capabilities: List[str]  # Required capabilities (e.g., ["chat", "code"])
    context_size: int  # Maximum context tokens supported
    metadata: Dict[str, str]  # Arbitrary metadata

@dataclass
class ModelDescriptor:
    model_id: str        # Unique identifier (e.g., "primary")
    display_name: str    # Human-readable name
    model_family: str    # Model series (e.g., "CodeyPretrained")
    model_type: str      # Type (e.g., "llm", "hf", "custom")
    supported_services: List[str]  # Services this model supports
    context_length: int  # Maximum context tokens
    supports_tools: bool  # Whether model supports tool integration
    supports_embeddings: bool  # Embedding capabilities
    metadata: Dict[str, str]  # Arbitrary key-value pairs

# Example usage:
# descriptor = ModelDescriptor(
#     model_id="primary",
#     display_name="Primary Model",
#     model_family="CodeyPretrained",
#     model_type="llm",
#     supported_services=["chat", "code"],
#     context_length=8192,
#     supports_tools=True,
#     supports_embeddings=True,
#     metadata={"deploy": "true"}
# )
