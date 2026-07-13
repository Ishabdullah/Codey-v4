from dataclasses import dataclass
from typing import Dict, Optional
import time

@dataclass
class ResourceSnapshot:
    available_ram: int          # Available RAM in bytes
    used_ram: int               # Used RAM in bytes
    cpu_usage: float            # CPU usage percentage (0-100)
    battery_level: int          # Battery level percentage (0-100)
    charging: bool              # Whether device is charging
    thermal_state: str          # Thermal state string (e.g., "normal", "warm", "hot")
    network_available: bool     # Whether network is available
    timestamp: float            # Unix timestamp of snapshot
    metadata: Dict[str, str]    # Additional context/metadata

# Example usage:
# snapshot = ResourceSnapshot(
#     available_ram=2048*1024*1024,  # 2GB
#     used_ram=1024*1024*1024,       # 1GB
#     cpu_usage=25.5,
#     battery_level=85,
#     charging=True,
#     thermal_state="normal",
#     network_available=True,
#     timestamp=time.time(),
#     metadata={"platform": "android-termux"}
# )