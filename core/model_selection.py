from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ModelSelection:
    selected_model: str
    confidence: float
    reason: str
    alternatives: List[str]
    metadata: Dict[str, Any]
