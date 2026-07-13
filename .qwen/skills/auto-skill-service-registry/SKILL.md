---
name: service-registry
description: ServiceRegistry implementation pattern for centralized service discovery and plugin extensibility in Codey-v4
source: auto-skill
extracted_at: '2026-07-11T19:48:29.881Z'
---

# ServiceRegistry Implementation Pattern

This skill documents the ServiceRegistry pattern for centralized service discovery and plugin extensibility, implemented as part of Codey-v4's architectural foundation.

## Why ServiceRegistry

ServiceRegistry enables future plugin-based expansion by separating **service discovery** (what services are available) from **service selection** (which service should handle a request). This creates a clean foundation for a plugin architecture without changing current behavior.

## Implementation

### Core ServiceRegistry Class

```python
# core/service_registry.py
class ServiceRegistry:
    def __init__(self):
        self._services = {}  # Internal registry dict

    def register_service(self, name, service) -> None:
        """Register a service by name. Raises ValueError if already exists."""
        if name in self._services:
            raise ValueError(f"Service '{name}' already registered")
        self._services[name] = service

    def unregister_service(self, name) -> None:
        """Unregister a service. Raises ValueError if not found."""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not found")
        del self._services[name]

    def get_service(self, name):
        """Get service by name. Raises ValueError if not found."""
        if name not in self._services:
            raise ValueError(f"Service '{name}' not found")
        return self._services[name]

    def has_service(self, name) -> bool:
        """Check if service exists."""
        return name in self._services

    def list_services(self) -> list:
        """Return list of all registered service names."""
        return list(self._services.keys())
```

### Kernel Integration Pattern

```python
# core/kernel.py
from core.service_registry import ServiceRegistry
from core.model_manager import ModelManager
from core.resource_manager import ResourceManager

class Kernel:
    def __init__(self, orchestrator=None):
        self._service_registry = ServiceRegistry()
        self._initialize_services()

    def _initialize_services(self):
        """Register core services at startup."""
        self._service_registry.register_service("model", ModelManager())
        self._service_registry.register_service("resource", ResourceManager())
        self._service_registry.register_service("conversation", kernel.handle_request)
        self._service_registry.register_service("memory", memory)
        self._service_registry.register_service("embedding", get_embedding_model)
        # ... additional services

    def get_service(self, name):
        """Delegate to ServiceRegistry."""
        return self._service_registry.get_service(name)

    def model_management(self, action, *args, **kwargs):
        """Get service and delegate to action method."""
        return getattr(self._service_registry.get_service("model"), action)(*args, **kwargs)
```

## Service Integration Pattern

### Registering Services

Services should register themselves during Kernel initialization:

```python
def _initialize_services(self):
    # Import at runtime to avoid circular dependencies
    from core.embeddings import get_embedding_model
    from core.memory_v2 import memory
    
    self._service_registry.register_service("embedding", get_embedding_model)
    self._service_registry.register_service("memory", memory)
```

### Accessing Services

Components retrieve services through Kernel:

```python
# Get a service by name
model_service = kernel.get_service("model")

# Call action methods on the service
result = model_service.load_model("primary")

# Or use convenience methods
kernel.model_management("load_model", "primary")
```

## Service Discovery vs Service Selection

### Service Discovery (Current Phase)
- Services register themselves with the ServiceRegistry at startup
- Components query the registry to find available services
- Registry validates registration and provides access

### Service Selection (Future Phase)
- Kernel will analyze requests to determine which service should handle them
- Plugin modules can register new services dynamically
- Service routing logic will be added without changing service access patterns

## Registered Services

| Service Name | Implementation | Purpose |
|--------------|---------------|---------|
| model | ModelManager | Model lifecycle management |
| resource | ResourceManager | Device resource reporting |
| conversation | kernel.handle_request | Request handling and routing |
| memory | memory_v2 | Four-tier memory system |
| embedding | get_embedding_model | RAG encoder functionality |
| sessions | save_session/load_session | Session persistence |
| summarize | summarize_history | Context compression |
| coding | fix_file | Coding operations |
| planner | _request_daemon_plan | Task planning |

## Testing Integration

```python
# Verify services are registered
kernel = Kernel()
assert kernel.has_service("model")
assert kernel.has_service("resource")

# Verify service access works
services = kernel.list_services()
assert "model" in services
assert "resource" in services

# Verify service methods are callable
model = kernel.get_service("model")
assert hasattr(model, "load_model")
```

## Migration Considerations

### Backward Compatibility
- Existing `kernel.model_management()` calls unchanged
- Existing `kernel.memory_management()` calls unchanged
- All existing behavior preserved

### Forward Compatibility
- New services can be registered without modifying Kernel
- Plugin modules can add themselves to ServiceRegistry
- Service selection logic can be added later

### Architectural Benefits
1. **Single Source of Truth**: All services register through ServiceRegistry
2. **Clear Separation**: Services register (discovery) vs Kernel routes (selection)
3. **Plugin Ready**: External modules can register services dynamically
4. **Testable**: Easy to verify registry state in tests

## Verification Steps

1. ✅ ServiceRegistry class created with standard interface
2. ✅ Kernel owns exactly one ServiceRegistry instance
3. ✅ Core services registered during initialization
4. ✅ get_service/unregister/register methods working
5. ✅ list_services/has_service methods working
6. ✅ Existing service access patterns preserved
7. ✅ Documentation updated with service discovery explanation