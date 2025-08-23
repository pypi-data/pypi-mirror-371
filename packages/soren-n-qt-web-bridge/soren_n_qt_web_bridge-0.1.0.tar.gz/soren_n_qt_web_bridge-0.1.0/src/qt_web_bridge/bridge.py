"""
Clean Python-JavaScript bridge objects for WebView communication.

This module provides base bridge classes that handle communication
between Python backend and TypeScript frontend with minimal overhead
and clean separation of concerns.
"""

import json
from collections.abc import Callable
from typing import Any

from qtpy.QtCore import QObject, Signal, Slot


class WebViewBridge(QObject):
    """
    Base bridge class for Python-JavaScript communication.

    Provides common patterns for bidirectional communication:
    - Signals from Python to JavaScript (data push)
    - Slots for JavaScript to Python calls (RPC-style)
    - JSON serialization helpers
    - Error handling

    Subclass this to create domain-specific bridges.
    """

    # Common signals that most bridges will need
    data_updated = Signal(str)  # JSON data to frontend
    status_changed = Signal(str, str)  # id, status
    error_occurred = Signal(str)  # error message

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._error_callback: Callable[[str], None] | None = None

    def set_error_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for handling bridge errors."""
        self._error_callback = callback

    def _emit_error(self, message: str) -> None:
        """Emit error signal and call error callback if set."""
        self.error_occurred.emit(message)
        if self._error_callback:
            self._error_callback(message)

    def _safe_json_dumps(self, data: Any) -> str:
        """Safely serialize data to JSON string."""
        try:
            return json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            self._emit_error(f"JSON serialization error: {e}")
            return "{}"

    def _safe_json_loads(self, json_str: str) -> dict[str, Any]:
        """Safely deserialize JSON string to Python object."""
        try:
            result = json.loads(json_str)
            return result if isinstance(result, dict) else {}
        except (TypeError, ValueError) as e:
            self._emit_error(f"JSON parsing error: {e}")
            return {}

    @Slot(result=str)
    def get_bridge_info(self) -> str:
        """Return basic bridge information (available to JavaScript)."""
        info = {
            "bridge_type": self.__class__.__name__,
            "version": "1.0.0",
            "capabilities": self._get_capabilities(),
        }
        return self._safe_json_dumps(info)

    def _get_capabilities(self) -> list[str]:
        """Override in subclasses to list available capabilities."""
        return ["basic_communication"]

    @Slot(str)
    def log_message(self, message: str) -> None:
        """Handle log messages from JavaScript."""
        print(f"[WebView] {message}")

    @Slot(str)
    def handle_error(self, error_message: str) -> None:
        """Handle errors from JavaScript."""
        self._emit_error(f"JavaScript error: {error_message}")


class DataBridge(WebViewBridge):
    """
    Bridge for handling data synchronization between Python and JavaScript.

    Common use cases:
    - Asset lists, search results, user preferences
    - Real-time data updates
    - State synchronization
    """

    # Data-specific signals
    items_loaded = Signal(str)  # JSON array of items
    item_updated = Signal(str, str)  # item_id, JSON item data
    search_results = Signal(str)  # JSON search results

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._items: list[dict[str, Any]] = []
        self._items_by_id: dict[str, dict[str, Any]] = {}

    def _get_capabilities(self) -> list[str]:
        return ["data_sync", "search", "item_management"]

    def set_items(self, items: list[dict[str, Any]]) -> None:
        """Set items and notify frontend."""
        self._items = items
        self._items_by_id = {
            str(item["id"]): item for item in items if item.get("id") is not None
        }

        items_json = self._safe_json_dumps(items)
        self.items_loaded.emit(items_json)
        self.data_updated.emit(items_json)

    def update_item(self, item_id: str, item_data: dict[str, Any]) -> None:
        """Update specific item and notify frontend."""
        if item_id in self._items_by_id:
            self._items_by_id[item_id].update(item_data)

            # Update in main list
            for i, item in enumerate(self._items):
                if item.get("id") == item_id:
                    self._items[i] = self._items_by_id[item_id]
                    break

            item_json = self._safe_json_dumps(item_data)
            self.item_updated.emit(item_id, item_json)
        else:
            self._emit_error(f"Item not found: {item_id}")

    @Slot(result=str)
    def get_all_items(self) -> str:
        """Get all items (called from JavaScript)."""
        return self._safe_json_dumps(self._items)

    @Slot(str, result=str)
    def get_item(self, item_id: str) -> str:
        """Get specific item by ID."""
        item = self._items_by_id.get(item_id, {})
        return self._safe_json_dumps(item)

    @Slot(str)
    def request_search(self, query: str) -> None:
        """Handle search request from JavaScript (override in subclasses)."""
        # Default implementation: simple name/description search
        results = []
        query_lower = query.lower()

        for item in self._items:
            name = item.get("name", "").lower()
            description = item.get("description", "").lower()

            if query_lower in name or query_lower in description:
                results.append(item)

        results_json = self._safe_json_dumps(results)
        self.search_results.emit(results_json)

    def add_item(self, item: dict[str, Any]) -> None:
        """Add new item and notify frontend."""
        if "id" in item:
            self._items.append(item)
            self._items_by_id[item["id"]] = item

            item_json = self._safe_json_dumps(item)
            self.item_updated.emit(item["id"], item_json)

            # Refresh full list
            self.set_items(self._items)

    def remove_item(self, item_id: str) -> None:
        """Remove item and notify frontend."""
        if item_id in self._items_by_id:
            # Remove from dict
            del self._items_by_id[item_id]

            # Remove from list
            self._items = [item for item in self._items if item.get("id") != item_id]

            # Refresh full list
            self.set_items(self._items)
        else:
            self._emit_error(f"Item not found for removal: {item_id}")


class ActionBridge(WebViewBridge):
    """
    Bridge for handling user actions from JavaScript to Python.

    Common use cases:
    - Button clicks, form submissions
    - File operations, downloads
    - System integrations
    """

    # Action-specific signals
    action_requested = Signal(str, str)  # action_type, JSON params
    action_completed = Signal(str, str)  # action_id, JSON result

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._action_handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}

    def _get_capabilities(self) -> list[str]:
        return ["action_handling", "async_operations"]

    def register_action_handler(
        self, action_type: str, handler: Callable[[dict[str, Any]], Any]
    ) -> None:
        """Register handler for specific action type."""
        self._action_handlers[action_type] = handler

    @Slot(str, str)
    def execute_action(self, action_type: str, params_json: str) -> None:
        """Execute action from JavaScript."""
        try:
            params = self._safe_json_loads(params_json)
            handler = self._action_handlers.get(action_type)

            if handler:
                # Emit signal for external handling
                self.action_requested.emit(action_type, params_json)

                # Call handler
                result = handler(params)

                # Notify completion
                action_id = params.get("action_id", action_type)
                result_json = self._safe_json_dumps(result or {})
                self.action_completed.emit(action_id, result_json)

            else:
                self._emit_error(f"No handler registered for action: {action_type}")

        except Exception as e:
            self._emit_error(f"Action execution error: {e}")

    @Slot(result=str)
    def get_available_actions(self) -> str:
        """Get list of available action types."""
        actions = list(self._action_handlers.keys())
        return self._safe_json_dumps(actions)

    def trigger_action_result(self, action_id: str, result: dict[str, Any]) -> None:
        """Manually trigger action result (for async operations)."""
        result_json = self._safe_json_dumps(result)
        self.action_completed.emit(action_id, result_json)
