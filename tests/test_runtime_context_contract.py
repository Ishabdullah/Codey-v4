import sys
import os

# Add the project root to sys.path so we can import core modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.runtime_context import RuntimeContext


def test_runtime_context_initialization():
    """Test that RuntimeContext initializes with expected defaults."""
    ctx = RuntimeContext()
    assert ctx.request is None
    assert ctx.selection is None
    assert ctx.policy_decision is None
    assert ctx.resource_snapshot is None
    assert ctx.model_state is None
    assert ctx.session_info is None
    assert ctx.metadata == {}
    assert ctx._metadata_owners == {}


def test_metadata_ownership_single_owner():
    """Test setting metadata with a single owner works."""
    ctx = RuntimeContext()
    ctx.set_metadata("test_key", "value", "owner_a")
    assert ctx.get_metadata("test_key") == "value"
    assert ctx.metadata_owner("test_key") == "owner_a"
    assert ctx.metadata == {"test_key": "value"}
    assert ctx._metadata_owners == {"test_key": "owner_a"}


def test_metadata_ownership_same_owner_can_overwrite():
    """Test same owner can overwrite its own metadata."""
    ctx = RuntimeContext()
    ctx.set_metadata("test_key", "value1", "owner_a")
    ctx.set_metadata("test_key", "value2", "owner_a")
    assert ctx.get_metadata("test_key") == "value2"
    assert ctx.metadata_owner("test_key") == "owner_a"
    assert ctx.metadata == {"test_key": "value2"}
    assert ctx._metadata_owners == {"test_key": "owner_a"}


def test_metadata_ownership_different_owner_raises():
    """Test different owner cannot overwrite existing key."""
    ctx = RuntimeContext()
    ctx.set_metadata("test_key", "value1", "owner_a")
    try:
        ctx.set_metadata("test_key", "value2", "owner_b")
        assert False, "Expected ValueError for owner mismatch"
    except ValueError as e:
        assert "owned by 'owner_a'" in str(e)
        assert "cannot be overwritten by 'owner_b'" in str(e)
        # Ensure value unchanged
        assert ctx.get_metadata("test_key") == "value1"
        assert ctx.metadata_owner("test_key") == "owner_a"


def test_multiple_keys_different_owners():
    """Test multiple keys can be owned by different components."""
    ctx = RuntimeContext()
    ctx.set_metadata("key1", "val1", "owner_a")
    ctx.set_metadata("key2", "val2", "owner_b")
    assert ctx.get_metadata("key1") == "val1"
    assert ctx.metadata_owner("key1") == "owner_a"
    assert ctx.get_metadata("key2") == "val2"
    assert ctx.metadata_owner("key2") == "owner_b"
    assert ctx.metadata == {"key1": "val1", "key2": "val2"}
    assert ctx._metadata_owners == {"key1": "owner_a", "key2": "owner_b"}


def test_metadata_owner_none_for_unknown_key():
    """Test metadata_owner returns None for unknown key."""
    ctx = RuntimeContext()
    assert ctx.metadata_owner("unknown") is None
    assert ctx.get_metadata("unknown") is None


if __name__ == "__main__":
    test_runtime_context_initialization()
    test_metadata_ownership_single_owner()
    test_metadata_ownership_same_owner_can_overwrite()
    test_metadata_ownership_different_owner_raises()
    test_multiple_keys_different_owners()
    test_metadata_owner_none_for_unknown_key()
    print("All tests passed.")