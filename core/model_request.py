#!/usr/bin/env python3
"""
ModelRequest contract for Kernel-ModelManager communication.
Lightweight dataclass for model operation requests.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ModelRequest:
    """Request object for model operations (load, unload, info, list)."""
    action: str  # "load", "unload", "info", "list"
    model_name: Optional[str] = None
    parameters: Dict = None