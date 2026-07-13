from core.base_policy import BasePolicy
from core.policy_decision import PolicyDecision
from core.service_selection import ServiceSelectionResult
from core.runtime_context import RuntimeContext
from core.model_selection import ModelSelection


class CapabilityPolicy(BasePolicy):
    """Policy that checks model capabilities.

    This implementation follows Phase 2 constraints: it does **not** perform any
    real capability checks. It merely demonstrates the correct contract –
    inheriting from ``BasePolicy`` and returning a ``PolicyDecision`` – and shows
    where the required data would be inspected.

    The policy receives a ``ServiceSelectionResult`` and a ``RuntimeContext``
    (which may contain a ``ModelSelection``).  No global look‑ups, manager
    imports, or static calls are used.
    """

    def evaluate(
        self,
        selection_result: ServiceSelectionResult,
        runtime_context: RuntimeContext,
    ) -> PolicyDecision:
        """Evaluate the selection against model capability constraints.

        Args:
            selection_result: The result from ``DecisionEngine.select_service``.
            runtime_context: Transport object populated by the Kernel. May hold
                a ``ModelSelection`` in ``runtime_context.selected_model``.

        Returns:
            PolicyDecision – always allowed in this placeholder implementation.
            If ``ModelSelection`` is ``None`` the decision is a pass‑through.
        """
        # Retrieve the optional ModelSelection without any manager lookup.
        model_sel: ModelSelection | None = getattr(runtime_context, "selected_model", None)

        # Pass‑through behaviour when no model information is present.
        if model_sel is None:
            return PolicyDecision(
                approved_selection=selection_result.service_name,
                allowed=True,
                metadata={"reason": "no model selection – pass‑through"},
            )

        # Placeholder for future capability checks. Currently we simply approve.
        # Future logic would inspect ``model_sel`` (e.g., supports_tools,
        # supports_embeddings, context_length, etc.) against requirements
        # encoded in ``selection_result.metadata``.
        return PolicyDecision(
            approved_selection=selection_result.service_name,
            allowed=True,
            metadata={"model": model_sel.selected_model, "info": "capability check placeholder"},
        )
