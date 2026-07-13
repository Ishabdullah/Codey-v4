---
name: codey-planning-routing
description: Investigate and understand how codey-v4 routes between planning mode and direct conversation response
source: auto-skill
extracted_at: '2026-07-09T23:53:35.144Z'
---

# Understanding Codey-v4 Planning Mode Routing

This skill documents the investigation approach for understanding how codey-v4 decides whether to:
1. **Route to planning mode** (multi-step task decomposition via daemon planner)
2. **Route to direct response** (simple Q&A via 7B model)

## Key Architecture

### Entry Points
- **main.py**: `repl()` → `_run_with_plan()` — main routing logic
- **core/agent.py**: `run_agent()` — agent loop with `is_complex()` check for orchestrator
- **core/planner_service.py**: `get_plan()` — unified planning interface (daemon → orchestrator fallback)
- **core/orchestrator.py**: `is_complex()`, `is_conversational()` — heuristics for routing

### Planning Decision Flow

```
User Input → _run_with_plan()
    │
    ├─ Solo peer delegation? ("ask claude to X") → run_agent() directly
    │
    ├─ CONVERSATIONAL? (is_conversational()) → run_agent() directly (NEW CHECK)
    │
    ├─ Daemon available? → _try_daemon_plan() → plan steps → execute
    │
    └─ Fallback → orchestrator.plan_tasks() → TaskQueue → run_queue()
```

#
### New Conversational Detection (2026-07-09)

The system previously failed to distinguish question-style inputs from task-oriented requests. This resulted in routing simple questions to the daemon planner when they should bypass all planning.

```diff
- If peer delegation is enabled and message doesn't match solo debug pattern
+ if is_conversational(prompt):  # NEW check
+     return run_agent(...)
```

This guard uses the `is_conversational()` heuristic introduced in the latest routing logic to prevent unnecessary planner calls for Q&A interactions.

### Testing Implications

The updated routing prevents "Ask gemini to explain X" or "How does Y work?" type queries from triggering complex task decomposition. Test cases in `test_orchestration.py` now validate this behavior.

| Level | Model | Trigger | Purpose |
|-------|-------|---------|---------|
| **Daemon planner** | 0.5B (port 8081) or remote | `_try_daemon_plan()` | Fast, lightweight task decomposition |
| **Orchestrator** | 7B (recursive_infer) | `plan_tasks()` fallback | Rich context planning with KB retrieval |

### Key Functions

1. **`is_complex(message)`** (orchestrator.py:48)
   - Detects multi-step tasks needing orchestration
   - Returns True for: "create X and test", "build API with endpoints"
   - Returns False for: questions, short requests, conversational patterns

2. **`is_conversational(message)`** (orchestrator.py:75 — NEW)
   - Detects Q&A style input that should bypass ALL planning
   - Returns True for: "How does X work?", "What is Y?", "Can you explain Z?"
   - Returns False for: task-oriented messages with action verbs

3. **`_try_daemon_plan(prompt)`** (main.py:151)
   - Calls `core.planner_service._request_daemon_plan()`
   - Returns step list or None

4. **`_request_daemon_plan()`** (planner_service.py:53)
   - Tries daemon planner (0.5B on port 8081)
   - Falls back to orchestrator planner (7B recursive_infer)

## Investigation Approach

### Step 1: Trace the Routing Flow
Start from `main.py` REPL loop → `_run_with_plan()` → identify decision points.

### Step 2: Map Decision Logic
Document each branching condition:
- Solo peer delegation check
- Conversational check (NEW - add this)
- Daemon availability check
- Plan execution vs direct agent

### Step 3: Identify Missing Guards
The bug: **No conversational check before daemon planning**. Simple questions get sent to planner.

### Step 4: Implement Fix
Add `is_conversational()` check in `_run_with_plan()` before peer delegation logic.

## Reusable Patterns

### Adding Conversational Detection
```python
from core.orchestrator import is_conversational

def _run_with_plan(prompt, history, yolo, use_plan, no_plan):
    # NEW: Bypass planning for conversations
    if is_conversational(prompt):
        return run_agent(prompt, history, yolo=yolo, no_plan=True)

    # ... existing peer delegation logic
```

### Heuristic Design
- Action keywords → task (not conversation)
- Question starters + no action → conversation
- Conversational patterns → conversation (even with actions)
- Short messages (< 10 chars) → conversation

## Testing Strategy

Add test cases in `tests/test_orchestration.py`:
```python
def test_simple_question_skips_planning(self):
    msg = "How does the async event loop work?"
    result, _ = _run_with_plan(msg, [], yolo=False, use_plan=False)
    assert not any("Plan:" in s for s in result.splitlines())

def test_conversational_routing(self):
    for cli in ["ask gemini to explain CORS", "ask claude to review my code"]:
        result, _ = _run_with_plan(cli, [], yolo=False, use_plan=False)
        assert f"[Peer CLI —" in result
```