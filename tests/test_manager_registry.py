import sys
import os
import unittest

# Ensure project root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codey4.manager_registry import ManagerRegistry
from codey4.core.base_manager import BaseManager

class TestManagerRegistryContract(unittest.TestCase):
    def test_manager_registry_structure(self):
        registry = ManagerRegistry()
        self.assertEqual(len(registry.list_managers()), 0)
        
        class MockManager(BaseManager):
            def initialize(self): pass
            def shutdown(self): pass
            @property
            def name(self): return "mock"
        
        mock = MockManager()
        registry.register_manager("mock", mock)
        self.assertIn('mock', registry.list_managers())
        self.assertTrue(registry.has_manager('mock'))
        mgr = registry.get_manager('mock')
        self.assertIsInstance(mgr, BaseManager)
        self.assertTrue(hasattr(mgr, 'initialize'))
        self.assertTrue(hasattr(mgr, 'shutdown'))

    def test_manager_registry_exclusions(self):
        registry = ManagerRegistry()
        # Exclude services and policy/decision
        self.assertNotIn('conversation', registry.list_managers())
        self.assertNotIn('memory', registry.list_managers())
        self.assertNotIn('decision_engine', registry.list_managers())
        self.assertNotIn('policy_engine', registry.list_managers())

if __name__ == '__main__':
    unittest.main()