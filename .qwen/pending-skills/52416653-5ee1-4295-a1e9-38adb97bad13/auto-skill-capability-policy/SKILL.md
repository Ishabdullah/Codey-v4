---
name: capability-policy
description: Explain the implementation of Capability агент Policy in Codey-v4
source: auto-skill
extracted_at: '2026-07-13T01:34:12.000Z'
---

# CapabilityPolicy

The *CapabilityPolicy* is a first‑stage placeholder policy that **does not perform real capability checks** but demonstrates the correct contract and integration with the rest of the Codey‑v4 runtime.

## Key Architectural Rules

> 1. `CapabilityPolicy` **must** inherit from `BasePolicy`.
> 2. `BasePolicy.evaluate` takes two arguments: `ServiceSelectionResult` and `RuntimeContext` and **returns a `PolicyDecision`**.
> 3. The policy must **never** perform any manager or kernel lookups – it can only use the data passed to it.
> 4. If `RuntimeContext.selected_model` is `None`, the policy should pass through the selection unmodified.
> 5. In the placeholder implementation the policy always approves the request and simply forwards the service name and a minimal metadata payload.
> 6. Future capability checks (tools, embeddings, services, context length) will be added once the `ModelDescriptor` is exposed.

## Implementation Overview

```
class CapabilityPolicy(BasePolicy):
    def evaluate(self, selection_result: ServiceSelectionResult,
                 runtime_context: RuntimeContext) -> PolicyDecision:
        # Grab optional ModelSelection from the runtime context
        model_sel = getattr(runtime_context, 'selected_model', None)

        if model_sel is None:
            # Pass‑through – no model configured
            return PolicyDecision(
                approved_selection=selection_result.service_name,
                allowed=True,
                metadata={'reason': 'no model selection – pass‑through'},
            )

        # Placeholder logic – always allow, but expose the model name
        return PolicyDecision(
            approved_selection=selection_result.service_name,
            allowed=True,
            metadata={'model': model_sel.selected_model, 'info': 'capability check placeholder'},
        )
```

### Integration Steps
1. **Add the file**: `core/capability_policy.py` (already present).
2. **Update `BasePolicy`** to match the new signature.
3. **Register** the policy in whatever bootstrap code creates the `PolicyEngine` (e.g., in `kernel.py` or a dedicated setup file).
4. **Test** using `pytest`. Two tests are provided: a pass‑through when no model is selected and a normal approval when a `ModelSelection` is set.

## Test Summary
```text
$ python -m pytest tests/test_capability_policy.py -q
2 passed
```

## Remaining Future Work
* Add real capability checks once `ModelDescriptor` is available.
* Expand the metadata with Zambia detail about selected tools, embeddings, etc.
* Ensure `PolicyEngine` preserves the policy‑supplied metadata.

---
*End of skill*
