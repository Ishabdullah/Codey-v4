import sys
import os
import unittest

# Add the project root to sys.path so we can import codey4 modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codey4.service_registry import ServiceRegistry
from codey4.core.base_service import BaseService

class TestServiceRegistryContract(unittest.TestCase):
    def test_service_registry_structure(self):
        registry = ServiceRegistry()
        # Should start empty
        self.assertEqual(len(registry.list_services()), 0)
        
        # Register a service
        class MockService(BaseService):
            def initialize(self): pass
            def shutdown(self): pass
            @property
            def name(self): return "mock"
            def handle_request(self, request): return None
            
        mock_service = MockService()
        registry.register_service("mock", mock_service)
        
        # Verify service registration
        self.assertEqual(registry.list_services(), ["mock"])
        self.assertTrue(registry.has_service("mock"))
        
        # Verify service contract
        service = registry.get_service("mock")
        self.assertIsInstance(service, BaseService)
        self.assertTrue(hasattr(service, 'initialize'))
        self.assertTrue(hasattr(service, 'shutdown'))
        self.assertTrue(hasattr(service, 'handle_request'))

    def test_service_registry_exclusions(self):
        registry = ServiceRegistry()
        # Register all components to test exclusions
        from codey4.kernel import DecisionEngine, PolicyEngine
        from codey4.manager_registry import ManagerRegistry
        from codey4.model_manager import ModelManager
        from codey4.resource_manager import ResourceManager
        from codey4.core.base_manager import BaseManager
        
        # These should NOT be in ServiceRegistry
        self.assertNotIn('decision_engine', registry.list_services())
        self.assertNotIn('policy_engine', registry.list_services())
        self.assertNotIn('manager_registry', registry.list_services())
        self.assertNotIn('model', registry.list_services())
        self.assertNotIn('resource', registry.list_services())

if __name__ == '__main__':
    unittest.main()