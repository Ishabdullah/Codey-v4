from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .request import Request


class BaseClassifier(ABC):
    """Abstract interface for request classifiers.

    A classifier maps an incoming Request to a ClassificationResult without
    containing any runtime or inference logic itself. Implementations
    (rule-based, model-based, remote) inherit from this base and provide the
    actual classification strategy.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable identifier for this classifier."""
        ...

    @abstractmethod
    def classify(self, request: Request) -> "ClassificationResult":
        """Produce a classification for the given request."""
        ...


@dataclass
class ClassificationResult:
    """Lightweight metadata describing the outcome of a classification.

    This object carries no runtime logic; it is pure data passed between
    architectural layers (e.g. an IntentClassifier and a future DecisionEngine).
    """

    intent: str
    confidence: float
    candidate_services: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
