import sys
import os
import unittest

# Add the project root to sys.path so we can import codey4 modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codey4.kernel import Kernel

class TestLifecycle(unittest.TestCase):
    def test_kernel_initialize(self):
        kernel = Kernel()
        kernel.initialize()
        
        # Managers should be initialized
        managers = kernel.list_managers()
        self.assertIn('model', managers)
        self.assertIn('resource', managers)
        
        # Services should be initialized
        services = kernel.list_services()
        self.assertGreater(len(services), 0)

    def test_kernel_shutdown(self):
        kernel = Kernel()
        kernel.initialize()
        kernel.shutdown()
        
        # After shutdown, managers and services should be unregistered
        self.assertEqual(len(kernel.list_managers()), 0)
        self.assertEqual(len(kernel.list_services()), 0)

    def test_initialize_continues_on_failure(self):
        # Create a kernel where one component fails
        kernel = Kernel()
        
        # Mock a failing manager registration
        original_reg = kernel._manager_registry.register_manager
        def failing_reg(name, manager):
            if name == 'model':
                raise RuntimeError("Model manager failed")
            return original_reg(name, manager)
        kernel._manager_registry.register_manager = failing_reg
        
        # Should not raise, should continue with other managers
        kernel.initialize()
        
        # Resource manager should still be there
        self.assertIn('resource', kernel.list_managers())
        self.assertNotIn('model', kernel.list_managers())

    def test_shutdown_continues_on_failure(self):
        kernel = Kernel()
        kernel.initialize()
        
        # Mock a failing manager unregister
        original_unreg = kernel._manager_registry.unregister_manager
        def failing_unreg(name):
            if name == 'model':
                raise RuntimeError("Model manager shutdown failed")
            return original_unreg(name)
        kernel._manager_registry.unregister_manager = failing_unreg
        
        # Should not raise
        kernel.shutdown()
        
        # Resource should be cleaned up, model might remain
        self.assertNotIn('resource', kernel.list_managers())
        # Model might still be there due to failure
        # but shutdown should have attempted all

if __name__ == '__main__':
    unittest.main()