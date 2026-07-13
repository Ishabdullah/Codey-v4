class ServiceRegistry:
    def __init__(self):
        self._services = {}

    def register_service(self, name, service):
        if name in self._services:
            raise ValueError(f"Service \"{name}\" already registered")
        self._services[name] = service

    def unregister_service(self, name):
        if name not in self._services:
            raise ValueError(f"Service \"{name}\" not found")
        del self._services[name]

    def get_service(self, name):
        if name not in self._services:
            raise ValueError(f"Service \"{name}\" not found")
        return self._services[name]

    def has_service(self, name):
        return name in self._services

    def list_services(self):
        return list(self._services.keys())