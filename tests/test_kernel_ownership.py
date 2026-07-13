import sys
import os
import unittest

# Add the project root to sys.path so we can import codey4 modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codey4.kernel import Kernel
from codey4.service_registry import ServiceRegistry
from codey4.manager_registry import ManagerRegistry

class TestKernelOwnership(unittest.TestCase):
    def test_kernel_components(self):
        kernel = Kernel()
        # Verify required components are present
        self.assertIn('decision_engine', kernel.__dict__)
        self.assertIn('policy_engine', kernel.__dict__)
        self.assertIn('manager_registry', kernel.__dict__)
        self.assertIn('service_registry', kernel.__dict__)

    def test_no_services_in_kernel(self):
        kernel = Kernel()
        # Services should not be directly in kernel
        self.assertNotIn('conversation', kernel.__dict__)
        self.assertNotIn('memory', kernel.__dict__)
        self.assertNotIn('embedding', kernel.__dict__)

    def test_managers_in_manager_registry(self):
        kernel = Kernel()
        managers = kernel.manager_registry.list_managers()
        self.assertIn('model', managers)
        self.assertIn('resource', managers)

    def test_services_in_service_registry(self):
        kernel = Kernel()
        services = kernel.service_registry.list_services()
        self.assertIn('conversation', services)
        self.assertIn('memory', services)
        self.assertNotIn('model', services)  # Should be in managers
        self.assertNotIn('resource', services)  # Should be in managers

if __name__ == '__main__':
    unittest.main()