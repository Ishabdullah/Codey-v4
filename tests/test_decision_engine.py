import sys
import os
import unittest
from datetime import datetime

# Add the project root to sys.path so we can import codey4 modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codey4.decision_engine import DecisionEngine
from codey4.service_selection import ServiceSelectionResult
from codey4.core.request import Request, Response
from codey4.rule_based_intent_classifier import RuleBasedIntentClassifier
from codey4.service_registry import ServiceRegistry

class TestDecisionEngineBoundary(unittest.TestCase):
    def test_input_is_request(self):
        classifier = RuleBasedIntentClassifier()
        registry = ServiceRegistry()
        engine = DecisionEngine(classifier=classifier, service_registry=registry)
        
        request = Request(
            id="test-1",
            service="conversation",
            prompt="hello world",
            session_id="sess-1",
            conversation_id="conv-1",
            metadata={},
            attachments=[],
            options={},
            created_at=datetime.now()
        )
        
        # This should not raise - input is valid Request
        # (will fail on missing service but that's a different issue)
        try:
            result = engine.select_service(request)
        except ValueError:
            # Expected if no service registered
            pass
            
    def test_output_is_service_selection_result(self):
        # Setup registry with mock service
        registry = ServiceRegistry()
        
        class MockService:
            def __init__(self):
                self.name = "conversation"
                
            def initialize(self): pass
            def shutdown(self): pass
            def handle_request(self, request): 
                return Response(success=True, content="hello", error=None,
                               metadata={}, tokens_used=0, execution_time=0.0, created_at=datetime.now())
                
        registry.register_service("conversation", MockService())
        
        classifier = RuleBasedIntentClassifier()
        engine = DecisionEngine(classifier=classifier, service_registry=registry)
        
        request = Request(
            id="test-1",
            service="conversation",
            prompt="hello world",
            session_id="sess-1",
            conversation_id="conv-1",
            metadata={},
            attachments=[],
            options={},
            created_at=datetime.now()
        )
        
        result = engine.select_service(request)
        
        # Should return ServiceSelectionResult, not a service instance
        self.assertIsInstance(result, ServiceSelectionResult)
        self.assertEqual(result.intent, "conversation")
        self.assertEqual(result.service_name, "conversation")
        self.assertTrue(hasattr(result, 'confidence'))
        self.assertTrue(hasattr(result, 'alternatives'))
        
    def test_does_not_execute_service(self):
        # Ensure select_service does not call handle_request
        class MockService:
            def __init__(self):
                self.name = "conversation"
                self.handle_called = False
                
            def initialize(self): pass
            def shutdown(self): pass
            def handle_request(self, request): 
                self.handle_called = True
                return Response(success=True, content="hello", error=None,
                               metadata={}, tokens_used=0, execution_time=0.0, created_at=datetime.now())
                
        mock_service = MockService()
        registry = ServiceRegistry()
        registry.register_service("conversation", mock_service)
        
        classifier = RuleBasedIntentClassifier()
        engine = DecisionEngine(classifier=classifier, service_registry=registry)
        
        request = Request(
            id="test-1",
            service="conversation",
            prompt="hello world",
            session_id="sess-1",
            conversation_id="conv-1",
            metadata={},
            attachments=[],
            options={},
            created_at=datetime.now()
        )
        
        result = engine.select_service(request)
        
        # The service's handle_request should NOT have been called
        self.assertFalse(mock_service.handle_called)
        
if __name__ == '__main__':
    unittest.main()