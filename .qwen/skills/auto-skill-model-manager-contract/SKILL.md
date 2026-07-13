---
name: model-manager-contract
source: auto-skill
description: Complete ModelManager contract boundary ensuring clear separation of concerns
extracted_at: '2026-07-12T18:13:01.934Z'

## Skill Purpose

Establish and enforce clear architectural boundaries for ModelManager to ensure it remains an infrastructure-only component without decision-making responsibilities, while integrating with PolicyEngine, Kernel, and RuntimeContext for proper model selection validation.

## Key Components

### 1. ModelCatalog Contract
- Created `core/model_catalog.py` with lightweight `ModelInfo` dataclass
- Fields: `name`, `version`, `capabilities` (list), `context_size` (int), `metadata` (dict)
- Purpose: Pure data container for model metadata; no loading/inference/hardware checks
- Used by ModelManager to validate and store model information

### 2. ModelManager Interface Refinement
- Restricted ModelManager to pure infrastructure operations only:
  - Allowed: `register_model(ModelInfo)`, `list_models()`, `get_model_info(name)`, `load_model(name)`, `unload_model(name)`
  - Removed/prohibited: request classification, model selection based on prompts, policy application
- Ensured ModelManager lives only in ManagerRegistry (Kernel-owned), not ServiceRegistry
- Verified no direct access from Services or Kernel decision logic

### 3. ModelRequest Contract Evaluation
- Analyzed whether a request object between Kernel and ModelManager was needed
- Determined current architecture (Kernel coordinates via ManagerRegistry) suffices
- Concluded no separate ModelRequest contract required; ModelInfo passed directly

### 4. RuntimeContext Rules Enforcement
- Confirmed `selected_model` field only holds `ModelSelection` instances
- Ensured no selection logic resides in RuntimeContext (pure data container)
- Validated that only authorized components (Kernel via PolicyEngine) set `selected_model`

### 5. PolicyEngine Validation Boundary
- Modified PolicyEngine to accept and validate `ModelSelection` (in addition to ServiceSelectionResult)
- PolicyEngine only approves/rejects existing selections; never chooses models
- Added validation logic: check if selected_model exists, verify against policies if any
- Maintained pass-through behavior when no policies registered

### 6. Kernel Coordination Role
- Kernel orchestrates flow: ModelSelection → PolicyEngine validation → ModelManager execution
- Kernel never ranks models, inspects capabilities, or makes model decisions
- Kernel accesses ModelManager solely via ManagerRegistry for infrastructure operations
- Kernel delegates model loading/unloading to ModelManager after policy approval

### 7. Verification and Boundary Checks
- Confirmed ModelManager remains infrastructure-only (no decision methods)
- Verified ModelCatalog is data-only (no behavior)
- Ensured PolicyEngine validates but does not select (no model choice logic)
- Confirmed Kernel coordinates only (no direct model decisions)
- Validated Services remain model-agnostic (access via ServiceRegistry, not ModelManager)
- Checked for circular dependencies (none found)

## Approach and Experiential Learning

- **Initial Audit**: Examined existing ModelManager implementation revealed it already leaned toward infrastructure but retained some ambiguity (e.g., comments about future support). Needed explicit interface restriction.
- **ModelCatalog Creation**: Initially considered embedding metadata directly in ModelManager; shifted to separate contract for clarity and reuse after recognizing need for standardized model description across components.
- **PolicyEngine Integration**: Early assumption was PolicyEngine would handle both service and model selection; iterated to realize PolicyEngine should only validate preselected models, preserving DecisionEngine's sole responsibility for selection.
- **Kernel Coordination**: Tested various flows; settled on Kernel as coordinator that never makes decisions but delegates appropriately, reinforcing the architectural boundary.
- **Boundary Validation**: Through grep and file inspections, confirmed no Service or DecisionEngine directly accessed ModelManager; all access mediated through Kernel.get_manager().

## How to Apply This Skill

1. When adding new model-related functionality, verify it respects the ModelManager infrastructure-only contract.
2. Use ModelInfo dataclass in model_catalog.py for any model metadata exchange.
3. Ensure PolicyEngine only validates ModelSelection; never instantiate or populate it.
4. Access ModelManager exclusively through Kernel.get_manager("model") for lifecycle operations.
5. Never place model selection logic in RuntimeContext, ServiceRegistry, or DecisionEngine.
6. For future policy additions, implement validation in PolicyEngine.evaluate() without altering the selected_model choice.

## Outcome

Achieved a clean separation where:
- DecisionEngine selects service and may produce ModelSelection (via future extension)
- PolicyEngine validates ModelSelection against constraints
- ModelManager executes model lifecycle operations
- Kernel coordinates without decision-making
- Services remain oblivious to model specifics