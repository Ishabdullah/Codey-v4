# RuntimeContext Usage Contract

## Overview

`RuntimeContext` is a lightweight, pass-through data container that carries transient runtime information across the kernel request pipeline. It is **NOT** a service, manager, or business logic component.

## Purpose

- Carry request-scoped data between pipeline stages
- Avoid parameter bloat in method signatures
- Enable future extensions (memory state, resource snapshots, model state, session info)
- Provide controlled metadata updates via ownership tracking

## Ownership Rules

### Kernel (Owner: `request`)
- Creates `RuntimeContext` in `handle_request()`
- Sets `request` field with the incoming Request object
- Passes context through the pipeline
- **Cannot**: Replace the RuntimeContext, store global state, mutate unrelated fields

### DecisionEngine (Owner: `selection`)
- Receives context via Request.runtime_context
- May set `selection` field with `ServiceSelectionResult` data
- May add selection metadata via `set_metadata(key, value, "decision_engine")`
- **Cannot**: Replace RuntimeContext, overwrite Kernel-owned fields

### PolicyEngine (Owner: `policy_decision`)
- Receives context from DecisionEngine
- May set `policy_decision` field with `PolicyDecision` data
- May add policy metadata via `set_metadata(key, value, "policy_engine")`
- **Cannot**: Replace RuntimeContext, overwrite DecisionEngine-owned fields

### Services (Owner: `metadata`, `model_state`, `resource_snapshot`, `session_info`)
- Receive context via Request.runtime_context
- May read approved context information
- May add execution metadata via `set_metadata(key, value, "service_name")`
- May set service-specific state in appropriate fields
- **Cannot**: Replace RuntimeContext, mutate unrelated fields, access Kernel directly

## Field Ownership Matrix

| Field | Owner | Allowed Writers | Access Pattern |
|-------|-------|-----------------|----------------|
| `request` | Kernel | Kernel only | Read-only for others |
| `selection` | DecisionEngine | DecisionEngine only | Read-only for others |
| `policy_decision` | PolicyEngine | PolicyEngine only | Read-only for others |
| `resource_snapshot` | ResourceManager | ResourceManager via Kernel | Future use |
| `model_state` | ModelManager | ModelManager via Kernel | Future use |
| `session_info` | SessionService | SessionService | Future use |
| `metadata` | Shared | All (via set_metadata) | Ownership enforced |

## Metadata Ownership Enforcement

The `set_metadata(key, value, owner)` method prevents accidental overwrites:

```python
context.set_metadata("latency_ms", 42, "decision_engine")  # OK
context.set_metadata("latency_ms", 100, "policy_engine")  # Raises ValueError
context.set_metadata("latency_ms", 100, "decision_engine")  # OK (same owner)
```

## Boundary Violations (PROHIBITED)

1. **No direct Kernel dependency**: Services must NOT import `core.kernel`
2. **No circular imports**: All components import RuntimeContext, not vice versa
3. **No business logic**: RuntimeContext contains NO methods beyond metadata helpers
4. **No global state**: RuntimeContext is request-scoped, never stored globally
5. **No field mutation**: Components may only write to fields they own

## Safe Usage Patterns

### Kernel Usage
```python
# Create and populate context
runtime_context = RuntimeContext(request=request_dict)
request.runtime_context = runtime_context
```

### DecisionEngine Usage
```python
# Read context
request_data = context.request.get("prompt")

# Add selection metadata
context.set_metadata("selection_time_ms", elapsed_ms, "decision_engine")
```

### Service Usage
```python
# Read approved context
selection = context.selection
policy = context.policy_decision

# Add execution metadata
context.set_metadata("tokens_used", 1500, "conversation_service")
```

## Future Extensions

When adding future fields:

1. Define the owner component
2. Update this contract with the ownership rule
3. Add the field to RuntimeContext (or use metadata with ownership)
4. Update validation tests

## Validation Tests

See `tests/test_runtime_context_contract.py` for tests covering:
- Ownership enforcement in metadata
- Field isolation between components
- Error handling for violations

## Version History

- v1.0 (2026-07-12): Initial contract for Phase 1 pipeline