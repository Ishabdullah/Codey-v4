## v2.7.2 — ServiceRegistry Integration

- **ServiceRegistry Implementation**: Added new ServiceRegistry class that provides standardized service registration, discovery, and access through the Kernel
- **Kernel integration**: Kernel now manages the ServiceRegistry and registers core services (model, resource, conversation, memory, embedding) at startup
- **Service interface**: All services follow a consistent pattern - register at startup, access via `Kernel.get_service("service_name")`, delegate via action methods, with validation and error handling
- **Backward compatibility**: Existing service access patterns remain unchanged; new services can be added without breaking current functionality
- **Updated architecture.md**: Added Service Discovery vs Service Selection section explaining how ServiceRegistry enables plugin-based expansion while maintaining current behavior
- **Updated Python API docs**: Added comprehensive ServiceRegistry documentation with code examples showing how services are registered and accessed

This establishes the foundation for future plugin-based expansion by separating service discovery (what ServiceRegistry provides) from service selection (future Kernel responsibility).

## v2.7.2 — Context Management Rewrite

- **Smarter context compression**: Trigger moved from 75% → 55% of context window; drop target is 40%, giving real headroom for long sessions.
- **Sliding window drop**: Oldest unpinned turns are dropped first — no model call needed for the drop itself.
- **Pinned messages**: `write_file`, `patch_file`, `[ERROR]`, shell results, and existing summaries are never dropped or re-summarized.
- **0.5B micro-summary**: After dropping turns, the 0.5B model on port 8081 generates a ≤100-word "Previously:" summary of only what was dropped. Best-effort — silently skipped if port 8081 is unreachable.
- **No re-summarization**: An existing `[CONVERSATION SUMMARY]` is pinned and never fed back into another summary pass.
- **Fixed content truncation**: Removed the `[:300]` message truncation that was destroying tool output before the summarizer could see it.
- **Planner timeout increased**: `asyncio.wait_for` raised from 45 s → 180 s; HTTP timeout raised from 30 s → 165 s to match.