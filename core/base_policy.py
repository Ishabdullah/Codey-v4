from abc import ABC, abstractmethod
from core.service_selection import ServiceSelectionResult
from core.policy_decision import PolicyDecision
from core.runtime_context import RuntimeContext

class BasePolicy(ABC):
    @abstractmethod
    def evaluate(self, selection_result: ServiceSelectionResult, runtime_context: RuntimeContext) -> PolicyDecision:
        """
        Evaluate a service selection against policy rules.

        Args:
            selection_result: ServiceSelectionResult from DecisionEngine
            runtime_context: RuntimeContext containing model selection and other state

        Returns:
            PolicyDecision indicating approval and any metadata.
        """