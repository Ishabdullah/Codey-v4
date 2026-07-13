from abc import ABC, abstractmethod

class BaseManager(ABC):
    @abstractmethod
    def initialize(self):
        ...

    @abstractmethod
    def shutdown(self):
        ...

    @abstractmethod
    def status(self):
        ...

# This class defines the contract for all runtime managers