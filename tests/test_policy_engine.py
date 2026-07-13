import sys
import os
import unittest

# Add the project root to sys.path so we can import codey4 modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codey4.policy_engine import PolicyEngine
from codey4.service_selection import ServiceSelectionResult
from codey4.policy_decision import PolicyDecision

class TestPolicyEngineBoundary(unittest.TestCase):
    def test_input_is_service_selection_result(self):
        # PolicyEngine.evaluate takes ServiceSelectionResult
        result = ServiceSelectionResult(
            service_name="chat",
            intent="chat",
            confidence=0.9,
            alternatives=[],
            metadata={}
        )
        
        # Verify input acceptance
        policy_engine = PolicyEngine()
        self.assertTrue(hasattr(policy_engine, 'evaluate'))
        # This should not raise
        decision = policy_engine.evaluate(result)

    def test_output_is_policy_decision(self):
        policy_engine = PolicyEngine()
        result = ServiceSelectionResult(
            service_name="chat",
            intent="chat",
            confidence=0.9,
            alternatives=[],
            metadata={}
        )
        decision = policy_engine.evaluate(result)
        
        self.assertIsInstance(decision, PolicyDecision)
        self.assertTrue(hasattr(decision, 'approved_selection'))
        self.assertTrue(hasattr(decision, 'allowed'))
        self.assertTrue(hasattr(decision, 'metadata'))

    def test_services_selection_logic(self):
        # PolicyEngine should NOT select services
        policy_engine = PolicyEngine()
        self.assertFalse(hasattr(policy_engine, 'select_service'))

    def test_no_execution_methods(self):
        policy_engine = PolicyEngine()
        
        # Should not have methods that execute services or change state
        self.assertFalse(hasattr(policy_engine, 'execute_service'))
        self.assertFalse(hasattr(policy_engine, 'handle_request'))

    def test_policy_validation(self):
        # Current implementation is pass-through
        policy_engine = PolicyEngine()
        result = ServiceSelectionResult(
            service_name="chat",
            intent="chat",
            confidence=0.9,
            alternatives=[],
            metadata={}
        )
        decision = policy_engine.evaluate(result)
        
        # Validation logic exists but doesn't reject valid results
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.approved_selection, "chat")

if __name__ == '__main__':
    unittest.main()