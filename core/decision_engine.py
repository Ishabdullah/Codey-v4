class DecisionEngine:
    def __init__(self, classifier: BaseClassifier, service_registry: ServiceRegistry):
        self._classifier = classifier
        self._service_registry = service_registry

    def select_service(self, request: Request, **kwargs) -> BaseService:
        """Select a service based on the request.

        Parameters
        ----------
        request: Request
            The incoming request.
        **kwargs
            Optional runtime parameters. Currently unused but reserved for passing a RuntimeContext.
        """
        # Step 1: Classify the request
        classification_result = self._classifier.classify(request)
        intent = classification_result.intent

        # Step 2: Find matching service in registry
        service = self._service_registry.get_service(intent)
        if service is None:
            raise ValueError(f"No service found for intent: {intent}")

        return ServiceSelectionResult(service_name=service.name, intent=classification_result.intent, confidence=classification_result.confidence, alternatives=classification_result.alternatives, metadata=classification_result.metadata)

# Example usage:
# kernel.insert_decision_engine(DecisionEngine(classifier, service_registry))