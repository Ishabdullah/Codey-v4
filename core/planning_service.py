from datetime import datetime
from typing import Any, Dict, Optional
from core.base_service import BaseService
from core.request import Request, Response
from core.service_descriptor import ServiceDescriptor


class PlanningService(BaseService):
    """Service for task planning and decomposition."""

    def __init__(self, planner_func):
        self.planner_func = planner_func

    @property
    def name(self) -> str:
        return "planning"

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def descriptor(self) -> ServiceDescriptor:
        return ServiceDescriptor(
            name="planning",
            display_name="Planning",
            description="Task planning and step decomposition",
            version="1.0.0",
            capabilities=["plan", "decompose"],
            supported_intents=["plan", "decompose"],
            dependencies=[]
        )

    def handle_request(self, request: Request) -> Response:
        """Process planning request based on action in options."""
        action = request.options.get("action", "get_plan")
        params = request.options.get("params", {})

        try:
            if action in ("get_plan", "plan"):
                prompt = params.get("prompt", request.prompt)
                no_plan = params.get("no_plan", request.no_plan)
                project_context = params.get("project_context", "")
                plan = self.planner_func(prompt, no_plan=no_plan, project_context=project_context)
                result = plan

            else:
                return Response(
                    success=False,
                    content=None,
                    error=f"Unknown planning action: {action}",
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