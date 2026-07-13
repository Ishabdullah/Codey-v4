"""
ManagerRegistry for Codey-v4.

Central registry for manager lifecycle management.
Managers are infrastructure components owned by the Kernel,
not pluggable services.
"""

from typing import Dict, TypeVar, Generic
from core.base_manager import BaseManager

T = TypeVar('T', bound=BaseManager)


class ManagerRegistry:
    """
    Registry for manager infrastructure components.
    
    Managers are NOT services - they are core infrastructure
    owned and managed by the Kernel. This registry is
    separate from ServiceRegistry which manages pluggable services.
    """
    
    def __init__(self):
        self._managers: Dict[str, BaseManager] = {}

    def register_manager(self, name: str, manager: BaseManager):
        """
        Register a manager with the registry.
        
        Args:
            name: Unique name for the manager
            manager: Manager instance to register
            
        Raises:
            ValueError: If a manager with the given name is already registered
        """
        if name in self._managers:
            raise ValueError(f"Manager \"{name}\" already registered")
        self._managers[name] = manager

    def unregister_manager(self, name: str):
        """
        Unregister a manager from the registry.
        
        Args:
            name: Name of the manager to unregister
            
        Raises:
            ValueError: If no manager with the given name is registered
        """
        if name not in self._managers:
            raise ValueError(f"Manager \"{name}\" not found")
        del self._managers[name]

    def get_manager(self, name: str) -> BaseManager:
        """
        Get a manager by name from the registry.
        
        Args:
            name: Name of the manager to retrieve
            
        Returns:
            The manager instance
            
        Raises:
            ValueError: If no manager with the given name is registered
        """
        if name not in self._managers:
            raise ValueError(f"Manager \"{name}\" not found")
        return self._managers[name]

    def has_manager(self, name: str) -> bool:
        """
        Check if a manager is registered.
        
        Args:
            name: Name of the manager to check
            
        Returns:
            True if manager is registered, False otherwise
        """
        return name in self._managers

    def list_managers(self) -> list:
        """
        List all registered manager names.
        
        Returns:
            List of manager names
        """
        return list(self._managers.keys())