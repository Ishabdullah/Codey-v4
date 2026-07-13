from datetime import datetime
from typing import Any, Dict, Optional
from core.base_service import BaseService
from core.request import Request, Response
from core.service_descriptor import ServiceDescriptor


class MemoryService(BaseService):
    """Service for memory operations (working, project, long-term, episodic)."""

    def __init__(self, memory):
        self.memory = memory

    @property
    def name(self) -> str:
        return "memory"

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def descriptor(self) -> ServiceDescriptor:
        return ServiceDescriptor(
            name="memory",
            display_name="Memory",
            description="Four-tier memory system: working, project, long-term, episodic",
            version="1.0.0",
            capabilities=["load_file", "unload_file", "search", "build_context", "log_action"],
            supported_intents=["remember", "recall", "context"],
            dependencies=["embedding"]
        )

    def handle_request(self, request: Request) -> Response:
        """Process memory request based on action in options."""
        action = request.options.get("action")
        params = request.options.get("params", {})

        try:
            if action == "load_file":
                filepath = params.get("filepath")
                self.memory.load_file(filepath)
                result = f"Loaded {filepath}"

            elif action == "unload_file":
                filepath = params.get("filepath")
                self.memory.unload_file(filepath)
                result = f"Unloaded {filepath}"

            elif action == "search":
                query = params.get("query", "")
                limit = params.get("limit", 5)
                results = self.memory.longterm.search(query, limit)
                result = results

            elif action == "build_context":
                message = params.get("message", "")
                result = self.memory.working.build_file_block(message)

            elif action == "log_action":
                action_name = params.get("action", "")
                details = params.get("details", "")
                self.memory.episodic.log(action_name, details)
                result = "Action logged"

            elif action == "status":
                result = self.memory.status()

            elif action == "tick":
                self.memory.tick()
                result = "Advanced turn"

            elif action == "clear":
                self.memory.clear()
                result = "Memory cleared"

            elif action == "evict_stale":
                self.memory.evict_stale()
                result = "Evicted stale files"

            elif action == "list_files":
                result = self.memory.working.get_file_names()

            else:
                return Response(
                    success=False,
                    content=None,
                    error=f"Unknown memory action: {action}",
                    metadata={},
                    tokens_used=0,
                    execution_time=0.0,
                    created_at=datetime.now()
                )

            return Response(
                success=True,
                content=result,
                error=None,
                metadata={},
                tokens_used=0,
                execution_time=0.0,
                created_at=datetime.now()
            )

        except Exception as e:
            return Response(
                success=False,
                content=None,
                error=str(e),
                metadata={},
                tokens_used=0,
                execution_time=0.0,
                created_at=datetime.now()
            )