from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from core.resource_snapshot import ResourceSnapshot


@dataclass
class RuntimeContext:
    """
    Lightweight container for shared runtime information.
    Holds transient state that may be needed across service boundaries
    without embedding business logic or creating dependencies.
    """
    request: Optional[Dict[str, Any]] = None
    selection: Optional[Dict[str, Any]] = None
    policy_decision: Optional[Dict[str, Any]] = None
    resource_snapshot: Optional[ResourceSnapshot] = None
    model_state: Optional[Dict[str, Any]] = None
    session_info: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    _metadata_owners: Dict[str, str] = field(default_factory=dict)
    selected_model: Optional["ModelSelection"] = field(default=None, repr=False)

    # Architectural rule: selected_model should only contain a ModelSelection
    # created by an authorized component. No selection logic should be
    # added to RuntimeContext.

    def set_metadata(self, key: str, value: Any, owner: str) -> None:
        """Set a metadata entry ensuring ownership consistency.

        If the key is already owned by another component, raising a ValueError
        prevents accidental overwrite from unrelated owners.
        """
        current_owner = self._metadata_owners.get(key)
        if current_owner and current_owner != owner:
            raise ValueError(
                f"Metadata key '{key}' owned by '{current_owner}', "
                f"cannot be overwritten by '{owner}'"
            )
        if key not in self._metadata_owners:
            self._metadata_owners[key] = owner
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Any | None:
        return self.metadata.get(key)

    def metadata_owner(self, key: str) -> str | None:
        """Return the recorded owner of a metadata key, if any."""
        return self._metadata_owners.get(key)