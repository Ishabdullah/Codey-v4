from datetime import datetime
from core.base_service import BaseService
from core.request import Request, Response
from core.service_descriptor import ServiceDescriptor


class CodingService(BaseService):
    """Service for code generation and fixing operations."""

    def __init__(self, coder):
        # coder is a callable that takes a prompt and returns generated code or modifications
        self.coder = coder

    @property
    def name(self) -> str:
        return "coding"

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def descriptor(self) -> ServiceDescriptor:
        return ServiceDescriptor(
            name="coding",
            display_name="Coding",
            description="Generates or fixes code based on prompts",
            version="1.0.0",
            capabilities=["generate", "fix", "refactor"],
            supported_intents=["code_generation", "bug_fix"],
            dependencies=[]
        )

    def handle_request(self, request: Request) -> Response:
        """Process coding request using the provided coder callable."""
        try:
            prompt = request.prompt
            # Pass through any additional options to coder if needed
            generated = self.coder(prompt)
            return Response(
                success=True,
                content=generated,
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