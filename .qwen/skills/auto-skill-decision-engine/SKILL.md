---
name: decision-engine
description: How to create a lightweight runtime DecisionEngine that selects services based on intent
source: auto-skill
extracted_at: '2026-07-12T16:30:00.000Z'
---

### Overview
The *DecisionEngine* is a simple coordinator that sits inside the kernel. It receives a `Request`, asks a `BaseClassifier` for an intent, and then looks up the matching `BaseService` in the `ServiceRegistry`.  The DecisionEngine never registers itself with the registry and does not execute the service – it simply returns the service instance to the caller.

### Key Characteristics
1. **Dependency injection** – The constructor receives the classifier and the registry; it never creates them.
2. **No inheritance from `BaseService`** – This keeps intent routing separate from service execution.
3. **Pure routing logic** – Only `classify` and a registry lookup occur.
4. **Kernel ownership** – The kernel creates the engine once at bootstrap and exposes it via a private attribute.

### Implementation Steps
1. **Create the file** `core/decision_engine.py`.
2. **Define the class** with an `__init__` accepting `classifier: BaseClassifier` and `service_registry: ServiceRegistry`.
3. **Implement `select_service(self, request: Request) -> BaseService`**:
   - Call `self._classifier.classify(request)`.
   - Grab the `intent` from the resulting `ClassificationResult`.
   - Retrieve the accuracy‑grade service: `self._service_registry.get_service(intent)`.
   - Throw a `ValueError` if no service is found.
   - Return the located `BaseService`.
4. **Add the DecisionEngine to the kernel**:
   - In `core/kernel.py`, after setting up the service registry, instantiate:
     ```python
     self._decision_engine = DecisionEngine(
         classifier=self._classifier avis? ,
         service_registry=self._service_registry
     )
     ```
   - Expose a read‑only property `decision_engine` that returns this instance.
5. **Verify integration**:
   - Run the test suite or a quick manual run:
     ```python
     requestUR = Request(...)
     service = kernel.decision_engine.select_service(requestUR)
     # service should be the matching BaseService instance
     ```
   - Confirm that the registry still does not contain a service named `decision_engine` (e.g., `kernel.has_service('decision_engine')` raises).  

### Notes
- The DecisionEngine intentionally does *not* perform any policy, resource, or model selection – this is reserved for future kernel responsibilities.
- By keeping the engine out of the registry, the routing layer remains decoupled from the service registration concerns and can be swapped or mocked during tests.
