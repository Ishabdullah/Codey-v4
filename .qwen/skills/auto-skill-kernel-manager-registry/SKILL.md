--- 
name: kernel-manager-registry
source: auto-skill
description: Establish a dedicated ManagerRegistry for core infrastructure managers (models, resources) separate from ServiceRegistry

extracted_at: '2026-07-12T17:22:15.683Z'

## Skill Purpose

Implement a Kernel-owned ManagerRegistry to centralize management of core infrastructure components (models, resources) while strictly separating them from pluggable services registered in ServiceRegistry.

## Key Components

1. **ManagerRegistry Creation**
- Core class with methods to register/unregister managers
- Strict separation from ServiceRegistry
- Managers are Kernel-internal infrastructure

2. **Kernel Integration**
- Kernel initializes ManagerRegistry upfront
- Managers register through dedicated register_manager() method
- ServiceRegistry remains for services only

3. **Service Access Patterns**
- Services continue using get_service() for pluggable services
- Managers accessed via get_manager() method
- Resources/models accessed through dedicated manager interfaces

## Verification

- Tests confirm managers appear only in ManagerRegistry
- Services never access managers directly
- No overlap between ServiceRegistry and ManagerRegistry

## Outcome

Clear separation between core infrastructure (managed by Kernel) and pluggable services (discovered through ServiceRegistry), enabling flexible plugin architecture.