from abc import ABC, abstractmethod
from datetime import datetime
from core.base_service import BaseService
from core.request import Request, Response
from core.service_descriptor import ServiceDescriptor


class ConversationService(BaseService):
    """Service for handling conversation requests through the agent runner."""

    def __init__(self, agent_runner):
        self.agent_runner = agent_runner

    @property
    def name(self) -> str:
        return "conversation"

    def initialize(self):
        """Initialize the service (no-op for this adapter)."""
        pass

    def shutdown(self):
        """Shutdown the service (no-op)."""
        pass

    def descriptor(self) -> ServiceDescriptor:
        """Return service metadata."""
        return ServiceDescriptor(
            name="conversation",
            display_name="Conversation",
            description="Handles conversation requests through agent runner",
            version="1.0.0",
            capabilities=["chat", "dialogue", "context management"],
            supported_intents=["chat"]
        )

    def handle_request(self, request: Request) -> Response:
        """Process conversation request through agent runner."""
        # Extract required information
        prompt = request.prompt
        session_id = request.session_id
        conversation_id = request.conversation_id

        # Call existing agent runner
        response, history = self.agent_runner(
            prompt, history, yolo=request.yolo, use_plan=request.use_plan, no_plan=request.no_plan
        )

        # Create response
        return Response(
            success=True,
            content=response,
            error=None,
            metadata={"session_id": session_id, "conversation_id": conversation_id},
            tokens_used=0,
            execution_time=0.0,
            created_at=datetime.now()
        )