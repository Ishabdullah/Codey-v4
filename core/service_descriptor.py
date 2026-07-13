from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ServiceDescriptor:
    """Metadata descriptor for a runtime service."""
    name: str
    display_name: str
    description: str
    version: str
    capabilities: List[str]
    supported_intents: List[str]
    dependencies: Optional[List[str]] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []