#!/usr/bin/env python3
"""
ResourceDescriptor contract for Phase 2.
Represents a resource provider identity and metadata.
Pure data contract - no behavior.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class ResourceDescriptor:
    resource_id: str        # Unique identifier (e.g., "system", "cpu", "memory", "battery")
    display_name: str       # Human-readable name
    resource_type: str      # Type category (e.g., "system", "cpu", "memory", "battery", "storage")
    metadata: Dict[str, str]  # Arbitrary key-value pairs for provider-specific info

# Example usage:
# descriptor = ResourceDescriptor(
#     resource_id="system",
#     display_name="System Resources",
#     resource_type="system",
#     metadata={"provider": "psutil+sysfs", "platform": "android-termux"}
# )