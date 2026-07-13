from core.service_selection import ServiceSelectionResult
from core.runtime_context import RuntimeContext
from core.model_selection import ModelSelection
from core.policy_engine import PolicyEngine
from core.capability_policy import CapabilityPolicy


def test_pass_through_no_model():
    policy_engine = PolicyEngine()
    policy_engine.register_policy(CapabilityPolicy())
    sr = ServiceSelectionResult(service_name="example", intent="demo")
    rc = RuntimeContext()  # no selected_model
    decision = policy_engine.evaluate(sr, rc)
    assert decision.allowed
    assert decision.approved_selection == "example"


def test_approve_with_model():
    policy_engine = PolicyEngine()
    policy_engine.register_policy(CapabilityPolicy())
    sr = ServiceSelectionResult(service_name="example", intent="demo")
    rcPER = RuntimeContext()
    rcPER.selected_model = ModelSelection(selected_model="gpt-4", confidence=1.0, reason="test", alternatives=[], metadata={})
    decision = policy_engine.evaluate(sr, rcPER)
    assert decision.allowed
    assert decision.approved_selection == "example"
    assert decision.metadata["model"] == "gpt-4"
