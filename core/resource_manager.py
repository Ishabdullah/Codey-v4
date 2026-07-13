#!/usr/bin/env python3
"""
ResourceManager for Codey-v4 (Phase 2: Infrastructure layer).
Centralized resource information collector. The single source of truth
for runtime state. Does NOT make decisions - only reports state.

Designed for Android/Termux compatibility. Provides placeholders
for information that cannot currently be collected.
"""

import os
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from core.resource_descriptor import ResourceDescriptor
from core.resource_snapshot import ResourceSnapshot
from utils.logger import warning
from core.base_manager import BaseManager

# Optional psutil support
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class ResourceManager(BaseManager):
    """
    Collects and exposes device resource information for Codey-v4.

    This is a state-reporting service only - it does not make scheduling,
    thermal policy, or battery policy decisions. Those belong to future phases.
    """

    def __init__(self):
        """Initialize the resource manager."""
        self._monitor = None  # Lazy-loaded sysmon SystemMonitor
        self._last_generation_speed: float = 0.0
        self._last_generation_time: float = 0.0
        # Registry for resource descriptors
        self._resources: Dict[str, ResourceDescriptor] = {}

    def initialize(self):
        """Initialize the resource manager (no-op in Phase 2)."""
        pass

    def shutdown(self):
        """Shut down the resource manager (no-op in Phase 2)."""
        pass

    def status(self) -> dict:
        """Return a status snapshot of the resource manager."""
        snapshot = self.get_snapshot()
        return {
            "ram_available": snapshot.available_ram,
            "ram_used": snapshot.used_ram,
            "cpu_usage": snapshot.cpu_usage,
            "battery_level": snapshot.battery_level,
            "registered_resources": len(self._resources)
        }

    # === Resource Registry Interface ===

    def register_resource(self, resource_descriptor: ResourceDescriptor) -> None:
        """
        Register a resource provider's metadata information.
        Used to track available resource providers.
        """
        self._resources[resource_descriptor.resource_id] = resource_descriptor

    def list_resources(self) -> list:
        """
        List all registered resource IDs.
        """
        return list(self._resources.keys())

    def get_resource_descriptor(self, resource_id: str) -> Optional[ResourceDescriptor]:
        """
        Get the resource descriptor for a given resource ID.
        """
        return self._resources.get(resource_id)

    # === Resource Snapshot Interface ===

    def get_snapshot(self) -> ResourceSnapshot:
        """
        Get current resource snapshot.
        Phase 2: returns current values from existing collection methods.
        """
        # Collect current resource data using existing methods
        available_ram = self.get_available_ram()
        total_ram = self.get_total_ram()
        used_ram = max(0, total_ram - available_ram)  # Calculate used RAM
        
        return ResourceSnapshot(
            available_ram=available_ram,
            used_ram=used_ram,
            cpu_usage=self.get_cpu_usage(),
            battery_level=self.get_battery_level() or 0,  # Default to 0 if None
            charging=self.get_battery_state() == "charging",
            thermal_state=self._get_thermal_state_string(),
            network_available=self._is_network_available(),
            timestamp=time.time(),
            metadata={
                "platform": "android-termux",
                "has_psutil": str(HAS_PSUTIL)
            }
        )

    # ── Memory Interfaces ────────────────────────────────────────────────────

    def get_available_ram(self) -> int:
        """
        Get available RAM in bytes.

        Uses psutil if available, falls back to /proc/meminfo on Linux/Termux.
        """
        try:
            if HAS_PSUTIL:
                return psutil.virtual_memory().available
            # Fallback: /proc/meminfo
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        # Value is in kB, convert to bytes
                        return int(line.split()[1]) * 1024
        except Exception:
            pass
        return 0

    def get_total_ram(self) -> int:
        """
        Get total RAM in bytes.

        Uses psutil if available, falls back to /proc/meminfo on Linux/Termux.
        """
        try:
            if HAS_PSUTIL:
                return psutil.virtual_memory().total
            # Fallback: /proc/meminfo
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        # Value is in kB, convert to bytes
                        return int(line.split()[1]) * 1024
        except Exception:
            pass
        return 0

    def get_ram_usage_percent(self) -> float:
        """Get RAM usage as percentage (0-100)."""
        try:
            if HAS_PSUTIL:
                return psutil.virtual_memory().percent
        except Exception:
            pass
        return 0.0

    # ── CPU Interfaces ───────────────────────────────────────────────────────

    def get_cpu_usage(self) -> float:
        """
        Get CPU usage percentage.

        Uses sysmon SystemMonitor for consistent readings,
        falls back to psutil or /proc/stat.
        """
        try:
            monitor = self._get_monitor()
            snap = monitor.snapshot if monitor else {}
            if snap and "cpu" in snap:
                return snap["cpu"]
        except Exception:
            pass

        # Fallback
        try:
            if HAS_PSUTIL:
                return psutil.cpu_percent(interval=0.1)
        except Exception:
            pass

        return 0.0

    def get_cpu_temperature(self) -> Optional[float]:
        """
        Get CPU/SoC temperature in Celsius.

        On Android/Termux, reads from /sys/class/thermal/thermal_zone*.
        Returns None if temperature cannot be determined.
        """
        try:
            monitor = self._get_monitor()
            snap = monitor.snapshot if monitor else {}
            if snap and "temp" in snap:
                return snap["temp"]
        except Exception:
            pass

        # Direct fallback for Android/Termux
        try:
            for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
                try:
                    ztype = (zone / "type").read_text().strip().lower()
                    raw = int((zone / "temp").read_text().strip())
                    temp_c = raw / 1000.0
                    # Ignore absurd readings
                    if 0 < temp_c < 120:
                        if any(k in ztype for k in ("cpu", "soc", "package", "skin")):
                            return temp_c
                except Exception:
                    continue
        except Exception:
            pass

        return None

    # ── Battery Interfaces ───────────────────────────────────────────────────

    def get_battery_level(self) -> Optional[int]:
        """
        Get battery level percentage.

        On Android/Termux, reads from /sys/class/power_supply/battery/
        or via termux-battery-status command.
        Returns None if battery information cannot be determined.
        """
        try:
            monitor = self._get_monitor()
            snap = monitor.snapshot if monitor else {}
            if snap and "battery_pct" in snap:
                return snap["battery_pct"]
        except Exception:
            pass

        # Direct fallback for Android/Termux
        try:
            batt = Path("/sys/class/power_supply/battery")
            if batt.exists():
                pct = int((batt / "capacity").read_text().strip())
                return pct
        except Exception:
            pass

        # Try termux-battery-status
        try:
            import subprocess
            import json
            out = subprocess.run(
                ["termux-battery-status"],
                capture_output=True, text=True, timeout=2,
            )
            if out.returncode == 0 and out.stdout.strip():
                data = json.loads(out.stdout)
                return data.get("percentage")
        except Exception:
            pass

        return None

    def get_battery_state(self) -> str:
        """
        Get battery charging state.

        Returns: "charging", "discharging", "full", or "unknown"
        """
        try:
            monitor = self._get_monitor()
            snap = monitor.snapshot if monitor else {}
            if snap and "battery_pct" in snap:
                # Note: sysmon only reports charging bool, check directly
                pass
        except Exception:
            pass

        # Direct check for Android/Termux
        try:
            batt = Path("/sys/class/power_supply/battery")
            if batt.exists():
                status = (batt / "status").read_text().strip().lower()
                if status in ("charging", "discharging", "full"):
                    return status
        except Exception:
            pass

        # Try termux-battery-status
        try:
            import subprocess
            import json
            out = subprocess.run(
                ["termux-battery-status"],
                capture_output=True, text=True, timeout=2,
            )
            if out.returncode == 0 and out.stdout.strip():
                data = json.loads(out.stdout)
                status = data.get("status", "").lower()
                if status in ("charging", "discharging", "full"):
                    return status
        except Exception:
            pass

        return "unknown"

    # ── Storage Interfaces ───────────────────────────────────────────────────

    def get_storage_available(self, path: str = ".") -> int:
        """
        Get available storage at path in bytes.

        Uses os.statvfs on Linux/Termux, psutil as fallback.
        Returns 0 if cannot be determined.
        """
        try:
            st = os.statvfs(path)
            # Available space for non-root users
            return st.f_bavail * st.f_frsize
        except Exception:
            pass

        try:
            if HAS_PSUTIL:
                usage = psutil.disk_usage(path)
                return usage.free
        except Exception:
            pass

        return 0

    def get_storage_total(self, path: str = ".") -> int:
        """
        Get total storage at path in bytes.

        Returns 0 if cannot be determined.
        """
        try:
            st = os.statvfs(path)
            return st.f_blocks * st.f_frsize
        except Exception:
            pass

        try:
            if HAS_PSUTIL:
                usage = psutil.disk_usage(path)
                return usage.total
        except Exception:
            pass

        return 0

    # ── Context & Memory Usage Interfaces ───────────────────────────────────────

    def get_context_usage(self) -> tuple:
        """
        Get context window usage.

        Returns (used_tokens, max_tokens).
        """
        try:
            from core.tokens import get_context_usage
            return get_context_usage([])
        except Exception:
            pass
        return 0, 4096  # Default context size

    def get_loaded_model_memory(self) -> int:
        """
        Get memory used by loaded models in bytes.

        Placeholder: Currently model memory cannot be directly measured.
        Estimated based on model type in future phases.
        """
        return 0  # Placeholder - not implemented

    def get_process_memory(self) -> int:
        """
        Get the current process memory usage in bytes.
        """
        try:
            if HAS_PSUTIL:
                proc = psutil.Process(os.getpid())
                return proc.memory_info().rss
        except Exception:
            pass

        # Fallback: read from /proc
        try:
            with open(f"/proc/{os.getpid()}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        return int(line.split()[1]) * 1024  # Convert kB to bytes
        except Exception:
            pass

        return 0

    # ── Generation Speed Interface ───────────────────────────────────────────

    def get_generation_speed(self) -> float:
        """
        Get tokens per second from last generation.

        Returns average tokens/sec. Returns 0.0 if no prior generation.
        """
        try:
            from core.inference_v2 import last_tps
            if last_tps > 0:
                return last_tps
        except Exception:
            pass
        return 0.0

    def record_generation_speed(self, tps: float) -> None:
        """
        Record generation speed for future queries.

        Called by inference layer after generation completes.
        """
        self._last_generation_speed = tps
        self._last_generation_time = time.time()

    # ── System Summary Interface ─────────────────────────────────────────────

    def get_system_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive system resource summary.

        Returns a dict with all available resource information.
        """
        ram_avail = self.get_available_ram()
        ram_total = self.get_total_ram()

        return {
            "memory": {
                "available_bytes": ram_avail,
                "total_bytes": ram_total,
                "available_gb": round(ram_avail / 1024**3, 2) if ram_avail else 0,
                "total_gb": round(ram_total / 1024**3, 2) if ram_total else 0,
                "usage_percent": self.get_ram_usage_percent(),
            },
            "cpu": {
                "usage_percent": self.get_cpu_usage(),
                "temperature_c": self.get_cpu_temperature(),
            },
            "battery": {
                "level_percent": self.get_battery_level(),
                "state": self.get_battery_state(),
            },
            "storage": {
                "available_bytes": self.get_storage_available(),
                "total_bytes": self.get_storage_total(),
                "available_gb": round(self.get_storage_available() / 1024**3, 2),
                "total_gb": round(self.get_storage_total() / 1024**3, 2),
            },
            "model": {
                "loaded_model_memory_bytes": self.get_loaded_model_memory(),
                "process_memory_bytes": self.get_process_memory(),
            },
            "generation": {
                "tokens_per_second": self.get_generation_speed(),
            },
        }

    # ── Internal Helpers ───────────────────────────────────────────────────────

    def _get_monitor(self):
        """Lazy-load the sysmon SystemMonitor."""
        if self._monitor is None:
            try:
                from core.sysmon import get_monitor
                self._monitor = get_monitor()
            except Exception:
                pass
        return self._monitor

    def _get_thermal_state_string(self) -> str:
        """Convert temperature reading to thermal state string."""
        temp = self.get_cpu_temperature()
        if temp is None:
            return "unknown"
        elif temp < 50:
            return "normal"
        elif temp < 70:
            return "warm"
        elif temp < 85:
            return "hot"
        else:
            return "critical"

    def _is_network_available(self) -> bool:
        """Check if network is available."""
        try:
            # Simple check: see if we can resolve a host
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except Exception:
            return False


# Global resource manager instance
_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    global _manager
    if _manager is None:
        _manager = ResourceManager()
    return _manager


def reset_resource_manager():
    """Reset the global resource manager (for testing)."""
    global _manager
    _manager = None