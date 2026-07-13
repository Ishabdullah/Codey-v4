from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class ServiceSelectionResult:
    service_name: str
    intent: str
    confidence: float = 0.0
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)