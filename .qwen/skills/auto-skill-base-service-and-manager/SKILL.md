--- 
name: base-service-and-manager
description: Introduce BaseService and BaseManager interfaces to establish architectural contracts for services and managers in Codey-v4
source: auto-skill
extracted_at: '2026-07-11T22:11:21.763Z'

**Approach:**
1. Defined lightweight abstract interfaces for services and managers
2. Implemented contract patterns in core/base_service.py and core/base_manager.py
3. Updated kernel.py to manage services via ServiceRegistry
4. Modified ModelManager and ResourceManager to inherit from new interfaces
5. Added service delegation methods in kernel.py for unified access

**Why:**
- Enables modular service/manager development
- Creates clear API boundaries
- Facilitates future extension without breaking existing behavior
- Reduces coupling between components

**How to apply:**
1. Subclass BaseService for new runtime services
2. Inherit BaseManager for new resource managers
3. Register implementations in ServiceRegistry
4. Use kernel.get_service() for centralized access

This architectural step maintains backward compatibility while preparing for future services like planning or migration components.