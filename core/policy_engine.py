from core.policy_decision import PolicyDecision
from core.base_policy import BasePolicy
from core.service_selection import ServiceSelectionResult
from core.runtime_context import RuntimeContext
from core.model_selection import ModelSelection


class PolicyEngine:
    """Runtime policy evaluation infrastructure for Codey-v4."""

    def __init__(self):
        self._policies = []

    def register_policy(self, policy: BasePolicy):
        """Register a BasePolicy instance."""
        self._policies.append(policy)

    def evaluate(self, selection_result: ServiceSelectionResult, runtime_context: RuntimeContext) -> PolicyDecision:
        """
        Evaluate the ServiceSelectionResult against registered policies.

        Pass-through: with no policies, returns the selection unchanged and approved.

        Args:
            selection_result: ServiceSelectionResult from DecisionEngine
            runtime_context: Runtime context containing model selection and other state

        Returns:
            PolicyDecision with approved_selection and allowed flag
        """
        # If no policies registered, return pass-through decision
        if not self._policies:
            if hasattr(selection_result, 'service_name'):
                return PolicyDecision(
                    approved_selection=selection_result.service_name,
                    allowed=True,
                    metadata={}
                )
            return PolicyDecision(
                approved_selection=None,
                allowed=False,
                metadata={'reason': 'No valid service selection provided'}
            )

        # Evaluate against each registered policy
        last_decision = None
        for policy in self._policies:
            # Policies must return PolicyDecision
            decision = policy.evaluate(selection_result, runtime_context)
            last_decision = decision
            if not decision.allowed:
                return decision

        # If all policies approve, return the last policy decision (preserving
        # its metadata) so policy-provided context is not lost.
        if last_decision is not None:
            return last_decision

        # Fallback pass-through if no policy produced a decision.
        if hasattr(selection_result, 'service_name'):
            return PolicyDecision(
                approved_selection=selection_result.service_name,
                allowed=True,
                metadata={}
            )
        return PolicyDecision(
            approved_selection=None,
            allowed=False,
            metadata={'reason': 'No valid service selection provided'}
        )