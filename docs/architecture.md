# Architecture

## Kernel Layer (v4)

The Kernel is the central coordinator for Codey-v4. It serves as the single entry point that all system components communicate through.

### Current State (Phase 1)

In Phase 1, the Kernel is a **pass-through layer** with a ServiceRegistry foundation. It forwards all requests to the existing architecture without performing routing, scheduling, memory management, or model loading. This prepares the architecture for future expansion while maintaining exact behavioral compatibility.

The Kernel now contains a ServiceRegistry that registers core services (ModelManager, ResourceManager, etc.) but continues to delegate to existing services through pass-through methods. This establishes the foundation for future service discovery without changing current behavior.

### Future Evolution

The Kernel will eventually become responsible for:
- **Request handling** - routing user requests to appropriate services
- **Model management** - loading, unloading, and managing model instances
- **Memory management** - coordinating the four-tier memory system
- **Embedding service** - managing the embedding encoder lifecycle
- **Tool service** - orchestrating tool execution and resource access
- **Planner service** - coordinating task planning and execution
- **Conversation service** - managing session state and summarization
- **Coding service** - overseeing coding-related operations

### Service Discovery vs Service Selection

Service discovery (what ServiceRegistry provides) is the mechanism for registering and locating services by name. It answers "What services are available and how do I access them?"

Service selection (future Kernel responsibility) will determine which service should handle a particular request. It answers "Which service should process this user request?"

This separation prepares Codey for future plugin-based expansion:
1. **Service Discovery** (Phase 1): Services register themselves with the Kernel's ServiceRegistry at startup
2. **Service Selection** (Future): The Kernel will analyze requests and route them to appropriate services
3. **Plugin Architecture** (Future): External plugins can register services with the ServiceRegistry and be selected by the Kernel's routing logic

By separating these concerns, Codey can evolve from a monolithic architecture to a plugin-extensible system while maintaining backward compatibility.

---

## Updated System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   CLI Client (codey-v4)                 │
│  User commands · flags · task queries · /status         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      KERNEL LAYER                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Central coordinator (single entry point)        │  │
│  │  Routes requests to existing services            │  │
│  │  Future: will handle routing, scheduling, etc.   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   Planner        │ │   Memory         │ │   Tools          │
│  · Task queue    │ │  · Working       │ │  · Filesystem    │
│  · Dependencies  │ │  · Project       │ │  · Shell         │
│  · Recovery      │ │  · Long-term     │ │  · Search        │
│  · Background    │ │  · Episodic      │ │  · Git           │
└──────────────────┘ └──────────────────┘ └──────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     LLM Layer                           │
│  Port 8080 — Qwen2.5-Coder-7B (primary agent)          │
│  Port 8081 — Qwen2.5-0.5B (planner + summarizer)       │
│  Port 8082 — nomic-embed-text (RAG encoder)           │
│  /v1/chat/completions · ChatML · thermal management   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 State Store (SQLite)                    │
│  Persistent memory · task queue · episodic log           │
│  Model state · embeddings · checkpoints                  │
└─────────────────────────────────────────────────────────┘
```

---

## Service Integration Through Kernel

### Request Handling
- `Kernel.handle_request(prompt, history, yolo, use_plan, no_plan)`
- Delegates to the orchestrator which manages planning and agent execution
- Entry point for all user-initiated work

### Model Management
- `Kernel.model_management(action, *args)`
- Delegates to `loader_v2` for model loading/unloading
- Future: will manage model lifecycle and resource allocation

### Memory Management
- `Kernel.memory_management(action, *args)`
- Delegates to `memory_v2` and `context` services
- Future: will coordinate the four-tier memory system

### Embedding Service
- `Kernel.embedding_service(action, *args)`
- Delegates to `embeddings` module
- Future: will manage embedding encoder lifecycle

### Tool Service
- `Kernel.tool_service(action, *args)`
- Delegates to agent tool execution
- Future: will orchestrate tool access and resource management

### Planner Service
- `Kernel.planner_service(action, *args)`
- Delegates to `planner_service` / `plannd`
- Future: will coordinate task planning

### Conversation Service
- `Kernel.conversation_service(action, *args)`
- Delegates to `sessions` and `summarizer`
- Future: will manage session state and summarization

### Coding Service
- `Kernel.coding_service(action, *args)`
- Delegates to `agent`, `tdd`, `fixmode`
- Future: will oversee coding-related operations

---

## Kernel Module (core/kernel.py)

```python
from core.kernel import Kernel

# Initialize as single entry point
kernel = Kernel()

# All requests go through Kernel
response, history = kernel.handle_request(prompt, history)

# Service-specific delegation (currently pass-through)
kernel.model_management("load_primary")
kernel.memory_management("load_file", "script.py")
kernel.embedding_service("get_embedding", "query text")
```

---

## Memory System

Conversation context is managed across four tiers:

```
┌─────────────────────────────────────────┐
│  Working Memory (in-memory, evicted)    │
│  Currently edited files                 │
│  Cleared after each task completes      │
└─────────────────────────────────────────┘
              │
┌─────────────────────────────────────────┐
│  Project Memory (persistent)            │
│  CODEY.md, README.md                    │
│  Never evicted — loaded at daemon start │
└─────────────────────────────────────────┘
              │
┌─────────────────────────────────────────┐
│  Long-term Memory (embeddings)          │
│  768-dim vectors via nomic-embed        │
│  Semantic search via cosine similarity  │
└─────────────────────────────────────────┘
              │
┌─────────────────────────────────────────┐
│  Episodic Memory (action log)           │
│  Append-only log of all actions         │
│  SQLite via state store                 │
└─────────────────────────────────────────┘
```

### Context Compression

When in-context token usage hits 55% of the context window, Codey compresses history:

1. The 4 most recent messages are always kept intact.
2. Pinned messages (file writes, errors, existing summaries) are never dropped.
3. Oldest unpinned turns are dropped until usage falls to 40%.
4. The 0.5B model generates a ≤100-word "Previously:" summary of what was dropped.
5. An existing `[CONVERSATION SUMMARY]` is never re-summarized — it stays pinned.

This keeps the 7B model focused on current work without losing critical context.

---

## What Persists Between Sessions

This table covers exactly what Codey saves, where it lives, and how long it lasts — so you know what context the model actually has when you start a new session.

| What | Where | Survives restart? | Expires? | How to clear |
|------|-------|------------------|----------|--------------|
| Last 6 turns of conversation | `~/.codey_sessions/<project-hash>.json` | Yes | After 2 hours of inactivity | `/clear` in-chat or `codey-v4 --clear-session` |
| Project memory (`CODEY.md`) | `<project>/CODEY.md` | Yes | Never | Edit or delete the file manually |
| Action log (every tool call) | `~/.codey-v4/state.db` | Yes | Never (append-only) | Delete `~/.codey-v4/state.db` |
| Open files / working context | In-memory only | No | On exit | — |
| File undo history | In-memory only | No | On exit | — |
| Knowledge base embeddings | `~/.codey-v4/kb/` (if set up) | Yes | Never | `codey-v4 kb clear` |

### What Codey does NOT do

- **Does not learn from your conversations.** The RAG index only contains what you explicitly load with `/load`, `/read`, or the knowledge base pipeline — not anything you've said or typed.
- **Does not send data anywhere.** All state is local. The only exception is peer CLI escalation (Claude Code, Gemini CLI, Qwen CLI), which requires explicit confirmation before any files are shared.
- **Does not auto-recover deep context on large projects.** The session window is 6 turns (expires in 2 hours). For long-running projects, `CODEY.md` is the primary source of persistent context — if it is sparse or missing, Codey starts each session with limited knowledge of your project.

### Practical advice for larger projects

1. Run `/init` at the start of a project to generate `CODEY.md`. Keep it updated as the project grows — it is the single most important thing for cross-session accuracy.
2. Use `--no-resume` if you want to start a session completely fresh without the last 6 turns being loaded.
3. The action log (`state.db`) grows indefinitely. It is not used for inference — only for observability (`/history`). Safe to delete if it grows large.

---

## Three-Model Design

Codey-v4 runs three purpose-built models simultaneously, each on its own port:

| Model | Port | Role |
|-------|------|------|
| Qwen2.5-Coder-7B Q4_K_M | 8080 | Primary agent — coding, reasoning, tool use |
| Qwen2.5-0.5B Q8_0 | 8081 | Planner + conversation summarizer |
| nomic-embed-text-v1.5 Q4 | 8082 | Embedding encoder for RAG retrieval |

The 7B model handles all user-facing work. The 0.5B runs independently for task planning and context compression so the 7B never burns tokens managing its own context. The embedding model runs continuously to serve retrieval queries during inference.

---

## ResourceManager (Phase 3)

### Current State (Phase 3)

The ResourceManager is a **state-reporting service only**. It collects and exposes device resource information but does not make decisions. This prepares Codey for intelligent runtime decisions in later phases.

### Responsibilities

#### ResourceManager Responsibilities
- **Memory reporting**: `get_available_ram()`, `get_total_ram()`, `get_ram_usage_percent()`
- **CPU reporting**: `get_cpu_usage()`, `get_cpu_temperature()`
- **Battery reporting**: `get_battery_level()`, `get_battery_state()`
- **Storage reporting**: `get_storage_available()`, `get_storage_total()`
- **Context reporting**: `get_context_usage()`
- **Generation metrics**: `get_generation_speed()`
- **System summary**: `get_system_summary()`
- **Placeholders**: `get_loaded_model_memory()` (not implemented - memory cannot be directly measured)

#### Kernel Responsibilities
- **Central coordination**: Single entry point for all system components
- **Service delegation**: Routes requests to appropriate services
- **Resource access**: Owns exactly one ResourceManager; other services access resources through Kernel
- **No direct OS queries**: Kernel never directly queries the OS - all resource access flows through ResourceManager

#### ModelManager Responsibilities
- **Model lifecycle**: `load_model()`, `unload_model()`, `preload_model()`
- **State tracking**: `get_loaded_models()`, `get_active_model()`, `is_loaded()`
- **Future placeholders**: `suspend_model()`, `resume_model()`, `estimate_memory()`, `monitor_resources()`, `thermal_status()`, `battery_status()`
- **One-way dependency**: May read ResourceManager, but ResourceManager never controls ModelManager

### Communication Flow

```
┌─────────────────┐
│      Other      │
│    Services     │
└────────┬────────┘
         │
         │ resource_management(action)
         ▼
┌─────────────────────────────────────┐
│         KERNEL LAYER                │
│  ┌───────────────────────────────┐   │
│  │   ResourceManager (owned)     │   │
│  │   Single source of truth      │   │
│  └───────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         │ OS queries (only path)
         ▼
┌─────────────────────────────────────┐
│     OPERATING SYSTEM                 │
│  /proc/meminfo, /proc/stat          │
│  /sys/class/thermal, battery sysfs   │
│  termux-api commands                │
└─────────────────────────────────────┘
```

### Design Principles

1. **Separation of concerns**: ResourceManager only reports state - no scheduling, optimization, or policy decisions. This allows future phases to iterate on decision-making without changing state collection.

2. **Single source of truth**: All OS resource access flows through ResourceManager. No service should directly query `/proc`, `/sys`, or run external commands for resource data.

3. **One-way dependency**: ModelManager may read ResourceManager for information, but ResourceManager never controls ModelManager. This preserves the passive state-reporting nature.

4. **Phase-based evolution**: Phase 3 introduces architecture only. Phases 4+ will use this state for intelligent runtime decisions.

---

## Project Structure

```
~/codey-v4/
├── codey-v4                   # CLI client
├── codeyd4                    # Daemon manager
├── main.py                    # Entry point
├── core/
│   ├── kernel.py              # NEW: Central coordinator (pass-through)
│   ├── daemon.py              # Daemon core and Unix socket server
│   ├── daemon_config.py       # Configuration manager
│   ├── state.py               # SQLite state store
│   ├── task_executor.py       # Task execution with tool loop and recovery
│   ├── orchestrator.py        # Planning and agent orchestration
│   ├── planner_v2.py          # Internal task planner
│   ├── plannd.py              # 0.5B planner daemon and get_plan_from_7b
│   ├── planner_client.py      # Async interface to the planner
│   ├── summarizer.py          # Context compression (sliding window + 0.5B)
│   ├── background.py          # Background tasks and file watches
│   ├── filesystem.py          # Direct filesystem access
│   ├── memory_v2.py           # Four-tier memory system
│   ├── embeddings.py          # Embedding model integration
│   ├── inference_v2.py        # Chat completions inference
│   ├── inference_hybrid.py    # Chat completions HTTP backend
│   ├── context.py             # Context block assembly
│   ├── checkpoint.py          # Self-modification safety
│   ├── observability.py       # Self-state queries
│   ├── recovery.py            # Error recovery strategies
│   ├── thermal.py             # Thermal and battery management
│   ├── tokens.py              # Token estimation and usage bar
│   ├── peer_cli.py            # Peer CLI escalation manager
│   ├── peer_shell.py          # PTY/subprocess runners for peer CLIs
│   ├── learning.py            # Learning system coordinator
│   ├── preferences.py         # User preference learning
│   ├── voice.py               # TTS + STT via Termux:API
│   ├── linter.py              # Static analysis: ruff / flake8 / mypy / ast
│   └── githelper.py           # Git: branches, merge, conflict detection
├── tools/
│   ├── file_tools.py          # File operations
│   ├── patch_tools.py         # Patch / diff tools
│   ├── shell_tools.py         # Shell execution
│   ├── kb_scraper.py          # Knowledge base indexer
│   └── kb_semantic.py         # Semantic index builder
├── utils/
│   ├── config.py              # All configuration constants
│   └── logger.py              # Structured logging
├── prompts/
│   └── system_prompt.py       # Agent system prompt
└── docs/                      # This documentation
```

---

## Python API

### ServiceRegistry

The Kernel now manages a ServiceRegistry that serves as the central hub for service registration and discovery:

```python
from core.service_registry import ServiceRegistry
from core.model_manager import ModelManager
from core.resource_manager import ResourceManager

# Create and register services
registry = ServiceRegistry()

# Register core services
registry.register_service("model", ModelManager())
registry.register_service("resource", ResourceManager())
registry.register_service("conversation", kernel.handle_request)  # Forward to kernel's request handler
registry.register_service("memory", memory_v2)  # Memory service
registry.register_service("embedding", embedding_manager)

# Access services by name
model_service = registry.get_service("model")
resource_service = registry.get_service("resource")
```

### Service Interface Methods

Services must support the following interface for reliable communication:

```python
def register_service(name, service_instance):
    """Register a service by name with the registry."""
    pass

def unregister_service(name):
    """Unregister a service by name."""
    pass

def get_service(name):
    """Get a registered service by name, raising ValueError if not found."""
    pass

def has_service(name):
    """Check if a service is registered."""
    pass

def list_services():
    """Return list of all registered service names."""
    pass

# Standard service methods:
def action_call(self, action_name, *args, **kwargs):
    """Delegate action to the service's action method."""
    return getattr(self, action_name)(*args, **kwargs)
```

### Registry Responsibilities

The Kernel's ServiceRegistry owns the following responsibilities:
1. **Service Registration**: Maintaining a registry of all available services
2. **Lifecycle Management**: Registering services during Kernel initialization
3. **Dependency Mediation**: Providing services to other components through standardized access
4. **Registration Protection**: Preventing duplicate service registration that would break system assumptions
5. **Visibility**: Exposing service metadata through `list_services()` for system introspection

### Service Integration Pattern

All services follow a consistent pattern:
1. **Service Discovery**: Services register themselves with the Kernel's ServiceRegistry at startup
2. **Service Access**: Components retrieve services through `Kernel.get_service("service_name")`
3. **Action Delegation**: Components call action methods on services: `service.action(action_name, ...)`
4. **Validation**: Registry validates service registration before granting access
5. **Error Handling**: Missing services raise `ValueError` with descriptive messages

This pattern ensures:
- Uniform access to all services
- Clear separation of concerns
- Easy extension for future plugins
- Backward compatibility with existing architecture