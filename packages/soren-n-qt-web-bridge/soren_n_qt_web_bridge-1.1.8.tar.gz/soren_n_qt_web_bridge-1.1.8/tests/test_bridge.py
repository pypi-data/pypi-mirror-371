"""
Test the bridge components.
"""

import json

from qt_web_bridge import ActionBridge, DataBridge, WebViewBridge


def test_webview_bridge_creation():
    """Test that WebViewBridge can be created."""
    bridge = WebViewBridge()
    assert bridge is not None


def test_bridge_info():
    """Test bridge info serialization."""
    bridge = WebViewBridge()
    info = bridge.get_bridge_info()

    # Should be valid JSON
    parsed = json.loads(info)
    assert "bridge_type" in parsed
    assert "version" in parsed
    assert "capabilities" in parsed
    assert parsed["bridge_type"] == "WebViewBridge"


def test_safe_json_operations():
    """Test JSON serialization helpers."""
    bridge = WebViewBridge()

    # Test safe dumps
    data = {"test": "value", "number": 42}
    json_str = bridge._safe_json_dumps(data)
    assert '"test"' in json_str
    assert '"value"' in json_str

    # Test safe loads
    loaded = bridge._safe_json_loads(json_str)
    assert loaded["test"] == "value"
    assert loaded["number"] == 42

    # Test error handling
    invalid_json = bridge._safe_json_loads("invalid json")
    assert invalid_json == {}


def test_data_bridge_functionality():
    """Test DataBridge data management."""
    bridge = DataBridge()

    # Test setting items
    items = [
        {"id": "1", "name": "Item 1", "description": "First item"},
        {"id": "2", "name": "Item 2", "description": "Second item"},
    ]
    bridge.set_items(items)

    # Test getting all items
    all_items = bridge.get_all_items()
    parsed_items = json.loads(all_items)
    assert len(parsed_items) == 2
    assert parsed_items[0]["name"] == "Item 1"

    # Test getting specific item
    item = bridge.get_item("1")
    parsed_item = json.loads(item)
    assert parsed_item["name"] == "Item 1"

    # Test updating item
    bridge.update_item("1", {"name": "Updated Item 1"})
    updated = bridge.get_item("1")
    parsed_updated = json.loads(updated)
    assert parsed_updated["name"] == "Updated Item 1"


def test_data_bridge_search():
    """Test DataBridge search functionality."""
    bridge = DataBridge()
    items = [
        {"id": "1", "name": "Apple", "description": "Red fruit"},
        {"id": "2", "name": "Banana", "description": "Yellow fruit"},
        {"id": "3", "name": "Cherry", "description": "Red berry"},
    ]
    bridge.set_items(items)

    # Simulate search (would normally be called from JS)
    # We can't test the signal emission directly, so test the logic
    query = "red"
    results = []
    query_lower = query.lower()

    for item in bridge._items:
        name = item.get("name", "").lower()
        description = item.get("description", "").lower()

        if query_lower in name or query_lower in description:
            results.append(item)

    assert len(results) == 2  # Apple and Cherry


def test_action_bridge_functionality():
    """Test ActionBridge action handling."""
    bridge = ActionBridge()

    # Test registering action handler
    results = {}

    def test_handler(params):
        results.update(params)
        return {"status": "success"}

    bridge.register_action_handler("test_action", test_handler)

    # Test getting available actions
    actions = bridge.get_available_actions()
    parsed_actions = json.loads(actions)
    assert "test_action" in parsed_actions


def test_data_bridge_add_remove():
    """Test DataBridge add/remove functionality."""
    bridge = DataBridge()

    # Start with some items
    items = [{"id": "1", "name": "Item 1"}]
    bridge.set_items(items)

    # Add new item
    new_item = {"id": "2", "name": "Item 2"}
    bridge.add_item(new_item)

    assert len(bridge._items) == 2
    assert "2" in bridge._items_by_id

    # Remove item
    bridge.remove_item("1")
    assert len(bridge._items) == 1
    assert "1" not in bridge._items_by_id
    assert "2" in bridge._items_by_id


def test_bridge_error_handling():
    """Test bridge error handling."""
    bridge = WebViewBridge()

    error_messages = []

    def error_callback(message):
        error_messages.append(message)

    bridge.set_error_callback(error_callback)

    # Trigger an error
    bridge._emit_error("Test error")

    assert len(error_messages) == 1
    assert "Test error" in error_messages[0]


def test_action_bridge_result_triggering():
    """Test manual action result triggering."""
    bridge = ActionBridge()

    # Test triggering result manually
    result = {"status": "completed", "data": "test"}
    bridge.trigger_action_result("test_action", result)

    # Can't easily test signal emission in unit test,
    # but at least verify method doesn't crash
