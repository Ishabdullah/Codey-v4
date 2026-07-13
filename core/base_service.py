from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .request import Request, Response


    @abstractmethod
    def initialize(self):
        ...

    @abstractmethod
    def shutdown(self):
        ...
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def initialize(self):
        ...

    @abstractmethod
    def shutdown(self):
        ...

    @abstractmethod
    def handle_request(self, request):
        ...

# Optional: Add is_a_service property if needed

# Placeholder for future services to inherit from

# Example:
# class MyService(BaseService):
#     def handle_request(self, request):
#         ...

# This class defines the contract for all runtime services