#!/usr/bin/env python3
"""
ModelManager for Codey-v4 (Phase 1: Pass-through layer)
Centralized model lifecycle management service.

Modified to use ModelDescriptor contract for Phase 1 implementation.
"""

# Travel through interfaces, gradually centralize ownership
from core.loader_v2 import get_loader
from core.model_catalog import ModelInfo, ModelDescriptor
from core.model_selection import ModelSelection
from utils.logger import warning
from typing import Optional
from core.base_manager import BaseManager


class ModelManager(BaseManager):
    """
    Manages model loading, unloading, and lifecycle.
    Initially a pass-through to loader_v2 with ModelDescriptor support.
    """

    def __init__(self):
        """Initialize with the global loader instance."""
        self._loader = get_loader()
        self._loaded_models = set()  # Track loaded model names
        self._active_model = None  # Track currently active model
        # Registry for ModelDescriptor objects
        self._model_descriptors = {}

    def initialize(self):
        """Initialize the manager (no-op in Phase 1)."""
        pass

    def shutdown(self):
        """Shut down the manager, unloading any loaded models."""
        for model_name in list(self._loaded_models):
            self.unload_model(model_name)

    def status(self) -> dict:
        """Return a status snapshot of the manager."""
        return {
            "loaded_models": list(self._loaded_models),
            "active_model": self._active_model,
            "is_loaded": self.is_loaded(),
        }

    # === Required Model Lifecycle Interfaces ===

    def load_model(self, model_name: str) -> bool:
        """
        Load a model by name.
        Currently only supports "primary" model.
        """
        if model_name == "primary":
            result = self._loader.load_primary()
            if result:
                self._loaded_models.add("primary")
                self._active_model = "primary"
            return result
        # Future: support other models
        warning(f"Model '{model_name}' not supported in Phase 1")
        return False

    def unload_model(self, model_name: str) -> bool:
        """
        Unload a model by name.
        Currently only supports "primary" model.
        """
        if model_name == "primary":
            self._loader.unload()
            self._loaded_models.discard("primary")
            if self._active_model == model_name:
                self._active_model = None
            return True
        # Future: support other models
        warning(f"Model '{model_name}' not supported in Phase 1")
        return False

    # === Model Registry Interface ===

    def register_model(self, model_descriptor: ModelDescriptor) -> None:
        """
        Register a model's metadata information.
        Used to track model capabilities and properties.
        """
        self._model_descriptors[model_descriptor.model_id] = model_descriptor

    def get_model(self, model_name: str) -> ModelDescriptor:
        """
        Get the model descriptor for a given model name.
        """
        return self._model_descriptors.get(model_name)

    def list_models(self) -> list:
        """
        List all registered model names.
        """
        return list(self._model_descriptors.keys())

    def select_model(self) -> ModelSelection:
        """
        Select a model for use.
        Phase 1: returns a default model if available.
        """
        # For Phase 1, return the first registered model if any
        model_names = self.list_models()
        if model_names:
            default_model = model_names[0]
            return ModelSelection(
                selected_model=default_model,
                confidence=1.0,
                reason="Phase 1 default selection",
                alternatives=model_names[1:] if len(model_names) > 1 else [],
                metadata={}
            )
        else:
            # No models registered; return a placeholder
            return ModelSelection(
                selected_model="none",
                confidence=0.0,
                reason="No models registered",
                alternatives=[],
                metadata={}
            )

    def is_loaded(self, model_name: str = None) -> bool:
        """
        Check if a model is loaded.
        If model_name is None, checks if any model is loaded.
        """
        if model_name is None:
            return len(self._loaded_models) > 0
        return model_name in self._loaded_models

    def get_active_model(self) -> str:
        """
        Get the currently active model name.
        """
        return self._active_model

    def preload_model(self, model_name: str) -> bool:
        """
        Preload a model for faster access.
        Currently equivalent to load_model.
        """
        return self.load_model(model_name)

    def release_unused_models(self) -> int:
        """
        Release models that are not currently in use.
        Currently does nothing as only one model is used.
        Future: implement actual unused model detection.
        """
        # Placeholder for future implementation
        return 0

    # === Future Reserved Interfaces (placeholders) ===

    def suspend_model(self, model_name: str) -> bool:
        """
        Suspend a model (freeze state, reduce resource usage).
        Not implemented in Phase 1.
        """
        warning(f"suspend_model not implemented in Phase 1")
        return False

    def resume_model(self, model_name: str) -> bool:
        """
        Resume a suspended model.
        Not implemented in Phase 1.
        """
        warning(f"resume_model not implemented in Phase 1")
        return False

    def estimate_memory(self, model_name: str) -> int:
        """
        Estimate memory usage of a model in bytes.
        Not implemented in Phase 1.
        """
        warning(f"estimate_memory not implemented in Phase 1")
        return 0

    def estimate_load_time(self, model_name: str) -> float:
        """
        Estimate time to load a model in seconds.
        Not implemented in Phase 1.
        """
        warning(f"estimate_load_time not implemented in Phase 1")
        return 0.0

    def monitor_resources(self) -> dict:
        """
        Monitor resource usage (CPU, memory, GPU, etc).
        Not implemented in Phase 1.
        """
        warning(f"monitor_resources not implemented in Phase 1")
        return {}

    def thermal_status(self) -> dict:
        """
        Get thermal status (temperature, throttling, etc).
        Not implemented in Phase 1.
        """
        warning(f"thermal_status not implemented in Phase 1")
        return {}

    def battery_status(self) -> dict:
        """
        Get battery status (level, charging, etc).
        Not implemented in Phase 1.
        """
        warning(f"battery_status not implemented in Phase 1")
        return {}


# Global manager instance
_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    global _manager
    if _manager is None:
        _manager = ModelManager()
    return _manager


def reset_model_manager():
    """Reset the global model manager (for testing)."""
    global _manager
    if _manager:
        _manager = None