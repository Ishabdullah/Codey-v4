from core.service_registry import ServiceRegistry
from core.manager_registry import ManagerRegistry
from core.model_manager import ModelManager
from core.resource_manager import ResourceManager
from core.decision_engine import DecisionEngine
from core.request import Request
from core.runtime_context import RuntimeContext
from core.rule_based_intent_classifier import RuleBasedIntentClassifier
from core.policy_engine import PolicyEngine


class Kernel:
    def __init__(self, orchestrator=None):
        """
        Central coordinator for Codey-v4 (Phase 1: Pass-through layer)
        """
        self._orchestrator = orchestrator  # Existing request handler
        self._service_registry = ServiceRegistry()  # Service discovery for pluggable services
        self._manager_registry = ManagerRegistry()  # Manager infrastructure registry
        self._classifier = RuleBasedIntentClassifier()  # Intent classifier
        self._decision_engine = DecisionEngine(
            classifier=self._classifier,
            service_registry=self._service_registry
        )  # Runtime service selection coordinator
        self._policy_engine = PolicyEngine()
        self.logger = logging.getLogger(__name__)
        # Lifecycle methods will be called explicitly by user
        # Initialize managers and services via initialize()
        # Shutdown will clean up via shutdown()

    def initialize(self):
        try:
            self._initialize_managers()
        except Exception as e:
            self.logger.error(f"Manager initialization failed: {e}")

        try:
            self._initialize_services()
        except Exception as e:
            self.logger.error(f"Service initialization failed: {e}")

    
    def shutdown(self):
        try:
            for name in self._manager_registry.list_managers():
                try:
                    self._manager_registry.unregister_manager(name)
                except Exception as e:
                    self.logger.error(f"Manager {name} shutdown failed: {e}")

            for name in self._service_registry.list_services():
                try:
                    self._service_registry.unregister_service(name)
                except Exception as e:
                    self.logger.error(f"Service {name} shutdown failed: {e}")

    def _initialize_managers(self):
        """
        Initialize manager infrastructure by registering core managers.

        Managers are infrastructure components owned by the Kernel,
        NOT pluggable services registered in ServiceRegistry.
        """
        # Register ModelManager as a manager (infrastructure)
        self._manager_registry.register_manager("model", ModelManager())

        # Register ResourceManager as a manager (infrastructure)
        self._manager_registry.register_manager("resource", ResourceManager())

    def _initialize_services(self):
        """
        Initialize service interfaces by registering existing services.

        Managers (model, resource) are NOT registered here -
        they are infrastructure managed by ManagerRegistry.
        """
        # Register other services with adapters
        from core.agent import run_agent as agent_runner
        from core.conversation_service import ConversationService
        self._service_registry.register_service("conversation", ConversationService(agent_runner))

        from core.memory_v2 import memory
        from core.memory_service import MemoryService
        self._service_registry.register_service("memory", MemoryService(memory))

        from core.embeddings import get_embedding_model
        from core.embedding_service import EmbeddingService
        self._service_registry.register_service("embedding", EmbeddingService(get_embedding_model()))

        from core.sessions import save_session, load_session
        self._service_registry.register_service("sessions", lambda: (save_session, load_session))

        from core.summarizer import summarize_history
        self._service_registry.register_service("summarize", summarize_history)

        from core.fixmode import fix_file
        from core.coding_service import CodingService
        self._service_registry.register_service("coding", CodingService(fix_file))

        from core.planner_service import _request_daemon_plan
        from core.planning_service import PlanningService
        self._service_registry.register_service("planner", PlanningService(_request_daemon_plan))

    def handle_request(self, prompt, history, yolo, use_plan, no_plan):
        """
        Process requests through the new decision pipeline
        """
        # Create Request object with core parameters
        request = Request(
            id=f"req-{int(time.time() * 1000)}",
            service="placeholder",
            prompt=prompt,
            session_id="main",
            conversation_id="main",
            metadata={"history": history},
            attachments=[]
        )
        # Create RuntimeContext
        runtime_context = RuntimeContext(request=request)

        # Add RuntimeContext to Request
        self._orchestrator = orchestrator  # Existing request handler
        self._service_registry = ServiceRegistry()  # Service discovery for pluggable services
        self._manager_registry = ManagerRegistry()  # Manager infrastructure registry
        self._classifier = RuleBasedIntentClassifier()  # Intent classifier
        self._decision_engine = DecisionEngine(
            classifier=self._classifier,
            service_registry=self._service_registry
        )  # Runtime service selection coordinator
        self._policy_engine = PolicyEngine()
        # Lifecycle methods will be called explicitly by user
        # Initialize managers and services via initialize()
        # Shutdown will clean up via shutdown()

    def _initialize_managers(self):
        """
        Initialize manager infrastructure by registering core managers.
        
        Managers are infrastructure components owned by the Kernel,
        NOT pluggable services registered in ServiceRegistry.
        """
        # Register ModelManager as a manager (infrastructure)
        self._manager_registry.register_manager("model", ModelManager())

        # Register ResourceManager as a manager (infrastructure)
        self._manager_registry.register_manager("resource", ResourceManager())

    def _initialize_services(self):
        """
        Initialize service interfaces by registering existing services.
        
        Managers (model, resource) are NOT registered here -
        they are infrastructure managed by ManagerRegistry.
        """
        # Register other services with adapters
        from core.agent import run_agent as agent_runner
        from core.conversation_service import ConversationService
        self._service_registry.register_service("conversation", ConversationService(agent_runner))

        from core.memory_v2 import memory
        from core.memory_service import MemoryService
        self._service_registry.register_service("memory", MemoryService(memory))

        from core.embeddings import get_embedding_model
        from core.embedding_service import EmbeddingService
        self._service_registry.register_service("embedding", EmbeddingService(get_embedding_model()))

        from core.sessions import save_session, load_session
        self._service_registry.register_service("sessions", lambda: (save_session, load_session))

        from core.summarizer import summarize_history
        self._service_registry.register_service("summarize", summarize_history)

        from core.fixmode import fix_file
        from core.coding_service import CodingService
        self._service_registry.register_service("coding", CodingService(fix_file))

        from core.planner_service import _request_daemon_plan
        from core.planning_service import PlanningService
        self._service_registry.register_service("planner", PlanningService(_request_daemon_plan))

    def handle_request(self, prompt, history, yolo, use_plan, no_plan):
        """
        Process requests through the new decision pipeline
        """
        # Create Request object with core parameters
        request = Request(
            id=f"req-{int(time.time() * 1000)}",
            service="placeholder",
            prompt=prompt,
            session_id="main",
            conversation_id="main",
            metadata={"history": history},
            attachments=[]
        )
        # Create RuntimeContext
        runtime_context = RuntimeContext(request=request)

        # Add RuntimeContext to Request
        request.runtime_context = runtime_context

        # Step 1: DecisionEngine selects service (with RuntimeContext support)
        service_selection = self._decision_engine.select_service(request)

        # Step 2: PolicyEngine validates the service selection
        policy_decision = self._policy_engine.evaluate(service_selection)
        if not policy_decision.allowed:
            raise ValueError("Service selection rejected by PolicyEngine")
        approved_selection_name = policy_decision.approved_selection
        # Step 3: Get approved service from registry
        service = self._service_registry.get_service(approved_selection_name)

        # Step 4: Execute service
        response = service.execute(request)
        return response

    # === Service Interfaces (Delegation) ===

    def get_service(self, name):
        """
        Get a service by name from the ServiceRegistry
        """
        return self._service_registry.get_service(name)

    def has_service(self, name):
        """
        Check if a service exists
        """
        return self._service_registry.has_service(name)

    def list_services(self):
        """
        List all registered services
        """
        return self._service_registry.list_services()

    @property
    def decision_engine(self):
        """
        Access the runtime DecisionEngine (service selector, not a service)
        """
        return self._decision_engine

    @property
    def policy_engine(self):
        """
        Access the runtime PolicyEngine (policy infrastructure, not a service)
        """
        return self._policy_engine

    def model_management(self, action, *args, **kwargs):
        """
        Get Model manager from ManagerRegistry and delegate to it
        """
        model_manager = self.get_manager("model")
        return getattr(model_manager, action)(*args, **kwargs)

    def memory_management(self, action, *args, **kwargs):
        """
        Get Memory service from ServiceRegistry and delegate to it
        """
        memory_service = self.get_service("memory")
        return getattr(memory_service, action)(*args, **kwargs)

    def embedding_service(self, action, *args, **kwargs):
        """
        Get Embedding service from ServiceRegistry and delegate to it
        """
        embedding_service = self.get_service("embedding")
        return getattr(embedding_service, action)(*args, **kwargs)

    def tool_service(self, action, *args, **kwargs):
        """
        Get Conversation service from ServiceRegistry and delegate to it
        """
        conversation_service = self.get_service("conversation")
        return conversation_service(action, *args, **kwargs)

    def planner_service(self, action, *args, **kwargs):
        """
        Get Planner service from ServiceRegistry and delegate to it
        """
        planner_service = self.get_service("planner")
        return planner_service(action, *args, **kwargs)

    def conversation_service(self, action, *args, **kwargs):
        """
        Get Conversation service from ServiceRegistry and delegate to it
        """
        conversation_service = self.get_service("conversation")
        return conversation_service(action, *args, **kwargs)

    def coding_service(self, action, *args, **kwargs):
        """
        Get Coding service from ServiceRegistry and delegate to it
        """
        coding_service = self.get_service("coding")
        return coding_service(action, *args, **kwargs)

    def resource_management(self, action, *args, **kwargs):
        """
        Get Resource manager from ManagerRegistry and delegate to it
        """
        resource_manager = self.get_manager("resource")
        return getattr(resource_manager, action)(*args, **kwargs)

    # === Manager Registry Access ===

    def get_manager(self, name):
        """
        Get a manager by name from the ManagerRegistry.
        Managers are infrastructure owned by the Kernel,
        distinct from pluggable services in ServiceRegistry.
        """
        return self._manager_registry.get_manager(name)

    def has_manager(self, name):
        """
        Check if a manager is registered in the ManagerRegistry.
        """
        return self._manager_registry.has_manager(name)

    def list_managers(self):
        """
        List all registered manager names.
        """
        return self._manager_registry.list_managers()

    @property
    def manager_registry(self):
        """
        Access the Kernel-owned ManagerRegistry.
        """
        return self._manager_registry
