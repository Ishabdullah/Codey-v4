from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PolicyDecision:
    approved_selection: str
    allowed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)