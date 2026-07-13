---
name: resource-manager-architecture
description: Architecture design and implementation of ResourceManager as single source of truth for device resource state
source: auto-skill
extracted_at: '2026-07-11T18:44:45.008Z'
---

# ResourceManager Architecture Implementation

This skill documents the Phase 3 architecture work introducing a centralized ResourceManager as the single source of truth for runtime resource state in Codey-v4.

## Architecture Overview

### Component Hierarchy

```
Kernel (Central Coordinator)
    └── ResourceManager (owned)
            │
            ├── /proc/meminfo, /proc/stat
            ├── /sys/class/thermal/
            ├── /sys/class/power_supply/battery/
            ├── termux-battery-status
            ├── os.statvfs()
            └── llama-server metrics (TPS)
```

### Key Design Decisions

1. **Passive State Reporting Only**: ResourceManager never makes scheduling, optimization, or policy decisions
2. **Single Source of Truth**: All OS resource queries flow through ResourceManager
3. **One-Way Dependency**: ModelManager may read ResourceManager; ResourceManager never controls ModelManager
4. **Phase-Gated**: Phase 3 = architecture only; Phase 4+ = decision-making on this state

## Implementation Details

### ResourceManager Interfaces

| Method | Data Source | Android/Termux Notes |
|--------|-------------|---------------------|
| `get_available_ram()` | psutil → /proc/meminfo | MemAvailable (kB) |
| `get_total_ram()` | psutil → /proc/meminfo | MemTotal (kB) |
| `get_cpu_usage()` | sysmon.SystemMonitor → psutil → /proc/stat | Delta calculation |
| `get_cpu_temperature()` | sysmon → /sys/class/thermal/ | Scan thermal_zone* for cpu/soc |
| `get_battery_level()` | sysmon → /sys/class/power_supply/battery/ → termux-battery-status | capacity + status files |
| `get_battery_state()` | Direct sysfs read | charging/discharging/full |
| `get_storage_available(path)` | os.statvfs() | f_bavail * f_frsize |
| `get_storage_total(path)` | os.statvfs() | f_blocks * f_frsize |
| `get_context_usage()` | tokens.get_context_usage() | Token estimation heuristic |
| `get_loaded_model_memory()` | Placeholder (returns 0) | Cannot measure directly |
| `get_process_memory()` | psutil → /proc/pid/status | VmRSS |
| `get_generation_speed()` | inference_v2.last_tps | Updated after each generation |
| `get_system_summary()` | Aggregates all above | Complete state snapshot |

### Kernel Integration

```python
# core/kernel.py
from core.resource_manager import get_resource_manager

class Kernel:
    def __init__(self, orchestrator=None):
        self._resource_manager = get_resource_manager()  # Owned instance
    
    def resource_management(self, action, *args, **kwargs):
        # Single gate for all resource queries
        return getattr(self._resource_manager, action)(*args, **kwargs)
```

Services call `kernel.resource_management("get_cpu_usage")` instead of direct OS access.

### Placeholder Documentation

Methods returning 0/None are **documented placeholders** for future phases:
- `get_loaded_model_memory()` — cannot measure model RSS separately from process
- `get_generation_speed()` — only available after first generation
- `get_battery_state()` — depends on termux-api availability

## Migration Log (Phase 3)

| Change | File | Reason |
|--------|------|--------|
| Created ResourceManager | `core/resource_manager.py` | Centralize all OS resource queries |
| Kernel owns ResourceManager | `core/kernel.py` | Enforce single source of truth |
| resource_management() interface | `core/kernel.py` | Gatekeeper pattern for all resource access |
| Architecture docs updated | `docs/architecture.md` | Document flow and design principles |

## Verification Checklist

- [x] ResourceManager implementation complete
- [x] All required interfaces implemented
- [x] Placeholders documented with rationale
- [x] Kernel integration verified
- [x] No behavioral changes to existing functionality
- [x] Architecture documentation updated
- [x] Migration log created

## Future Phase Integration Points

Phase 4 will add decision-making on top of this state:
- `ThermalPolicy(resource_manager.get_cpu_temperature())`
- `BatteryPolicy(resource_manager.get_battery_level())`
- `ModelSwitcher(resource_manager.get_available_ram())`
- `Scheduler(resource_manager.get_system_summary())`

Each policy lives outside ResourceManager — it only reads, never writes.