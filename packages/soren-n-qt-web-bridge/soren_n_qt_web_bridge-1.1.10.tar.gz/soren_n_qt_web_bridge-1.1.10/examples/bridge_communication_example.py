#!/usr/bin/env python3
"""
Bridge Communication Example

This example demonstrates Python-JavaScript communication using
the bridge system in qt-webview-bridge.
"""

import json
import sys
from typing import Any

try:
    from qtpy.QtCore import QTimer, Slot
    from qtpy.QtWidgets import (
        QApplication,
        QMainWindow,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )

    from qt_web_bridge import ActionBridge, BridgedWebView, DataBridge
except ImportError as e:
    print(f"Required packages not available: {e}")
    print("Install with: pip install soren-n-qt-web-bridge[examples]")
    sys.exit(1)


class CustomDataBridge(DataBridge):
    """Custom data bridge with application-specific functionality."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_sample_data()

    def load_sample_data(self):
        """Load some sample data for demonstration."""
        sample_items = [
            {
                "id": "1",
                "name": "Desktop Application",
                "type": "Qt",
                "status": "active",
            },
            {"id": "2", "name": "Web Interface", "type": "React", "status": "loading"},
            {"id": "3", "name": "Mobile App", "type": "Flutter", "status": "planned"},
            {"id": "4", "name": "API Server", "type": "FastAPI", "status": "active"},
        ]
        self.set_items(sample_items)

    @Slot(str)
    def request_search(self, query: str):
        """Enhanced search with type filtering."""
        results = []
        query_lower = query.lower()

        for item in self._items:
            name_match = query_lower in item.get("name", "").lower()
            type_match = query_lower in item.get("type", "").lower()
            status_match = query_lower in item.get("status", "").lower()

            if name_match or type_match or status_match:
                results.append(item)

        results_json = self._safe_json_dumps(results)
        self.search_results.emit(results_json)


class CustomActionBridge(ActionBridge):
    """Custom action bridge with application-specific actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_action_handlers()

    def setup_action_handlers(self):
        """Setup custom action handlers."""
        self.register_action_handler("update_status", self.handle_update_status)
        self.register_action_handler("add_item", self.handle_add_item)
        self.register_action_handler("delete_item", self.handle_delete_item)
        self.register_action_handler("show_notification", self.handle_notification)

    def handle_update_status(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle status update requests."""
        item_id = params.get("item_id")
        new_status = params.get("status")

        print(f"[ACTION] Updating item {item_id} status to {new_status}")

        return {
            "success": True,
            "item_id": item_id,
            "old_status": "unknown",
            "new_status": new_status,
        }

    def handle_add_item(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle adding new items."""
        name = params.get("name", "New Item")
        item_type = params.get("type", "Unknown")

        print(f"[ACTION] Adding new item: {name} ({item_type})")

        return {
            "success": True,
            "item": {
                "id": f"new_{len(params)}",
                "name": name,
                "type": item_type,
                "status": "created",
            },
        }

    def handle_delete_item(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle item deletion."""
        item_id = params.get("item_id")
        print(f"[ACTION] Deleting item {item_id}")

        return {"success": True, "deleted_id": item_id}

    def handle_notification(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle notification display."""
        message = params.get("message", "No message")
        level = params.get("level", "info")

        print(f"[NOTIFICATION] {level.upper()}: {message}")

        return {"success": True, "displayed": True}


class BridgeCommunicationWindow(QMainWindow):
    """Window demonstrating bridge communication."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bridge Communication Example")
        self.setGeometry(100, 100, 1400, 900)

        self.setup_ui()
        self.setup_webview()

        # Load content after brief delay
        QTimer.singleShot(200, self.load_content)

    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Control buttons
        button_layout = QVBoxLayout()

        self.add_data_btn = QPushButton("Add Random Data Item")
        self.add_data_btn.clicked.connect(self.add_random_item)
        button_layout.addWidget(self.add_data_btn)

        self.update_status_btn = QPushButton("Update Item Status")
        self.update_status_btn.clicked.connect(self.update_random_status)
        button_layout.addWidget(self.update_status_btn)

        layout.addLayout(button_layout)

        # WebView
        self.webview = BridgedWebView()
        layout.addWidget(self.webview)

    def setup_webview(self):
        """Setup WebView with bridges."""
        # Create custom bridges
        self.data_bridge = CustomDataBridge()
        self.action_bridge = CustomActionBridge()

        # Connect signals for monitoring
        self.data_bridge.items_loaded.connect(self.on_items_loaded)
        self.data_bridge.search_results.connect(self.on_search_results)
        self.action_bridge.action_completed.connect(self.on_action_completed)

        # Register bridges with WebView
        self.webview.register_bridge_object("data", self.data_bridge)
        self.webview.register_bridge_object("actions", self.action_bridge)

        # Set HTML content
        self.webview.set_dev_html_content(self.create_demo_html())

    def create_demo_html(self) -> str:
        """Create demonstration HTML with JavaScript bridge usage."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bridge Communication Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .section {
            background: #2d2d2d;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #444;
        }

        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        button {
            background: #007acc;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }

        button:hover {
            background: #005a9e;
        }

        button:disabled {
            background: #666;
            cursor: not-allowed;
        }

        input, select {
            background: #3d3d3d;
            border: 1px solid #555;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            margin: 5px;
        }

        .item-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }

        .item {
            background: #3d3d3d;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #555;
        }

        .item h4 {
            margin: 0 0 10px 0;
            color: #4fc3f7;
        }

        .status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }

        .status.active { background: #4caf50; }
        .status.loading { background: #ff9800; }
        .status.planned { background: #9c27b0; }
        .status.created { background: #2196f3; }

        #logs {
            background: #1e1e1e;
            border: 1px solid #444;
            padding: 15px;
            border-radius: 5px;
            max-height: 200px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Bridge Communication Demo</h1>

        <div class="section">
            <h2>JavaScript ↔ Python Communication</h2>
            <div class="controls">
                <button onclick="loadAllData()">Load All Data</button>
                <button onclick="searchData()">Search Data</button>
                <button onclick="addNewItem()">Add New Item</button>
                <button onclick="updateRandomStatus()">Update Status</button>
                <button onclick="testNotification()">Test Notification</button>
                <button onclick="clearLogs()">Clear Logs</button>
            </div>

            <input type="text" id="searchInput" placeholder="Search items..."
                   onkeyup="if(event.key==='Enter') searchData()">
        </div>

        <div class="section">
            <h2>Data Items</h2>
            <div id="itemGrid" class="item-grid">
                <!-- Items will be populated here -->
            </div>
        </div>

        <div class="section">
            <h2>Communication Logs</h2>
            <div id="logs"></div>
        </div>
    </div>

    <script>
        // Bridge communication functions
        function logMessage(message) {
            const logs = document.getElementById('logs');
            const timestamp = new Date().toLocaleTimeString();
            logs.innerHTML += `[${timestamp}] ${message}<br>`;
            logs.scrollTop = logs.scrollHeight;
        }

        function loadAllData() {
            logMessage('🔄 Requesting all data from Python...');
            try {
                const dataJson = data.get_all_items();
                const items = JSON.parse(dataJson);
                displayItems(items);
                logMessage(`✅ Loaded ${items.length} items from Python`);
            } catch (error) {
                logMessage(`❌ Error loading data: ${error}`);
            }
        }

        function searchData() {
            const query = document.getElementById('searchInput').value;
            if (!query.trim()) {
                loadAllData();
                return;
            }

            logMessage(`🔍 Searching for: "${query}"`);
            data.request_search(query);
        }

        function addNewItem() {
            const name = prompt('Enter item name:', 'New Project');
            const type = prompt('Enter item type:', 'Web App');

            if (name && type) {
                logMessage(`➕ Adding new item: ${name} (${type})`);
                const params = {
                    action_id: 'add_' + Date.now(),
                    name: name,
                    type: type
                };
                actions.execute_action('add_item', JSON.stringify(params));
            }
        }

        function updateRandomStatus() {
            const statuses = ['active', 'loading', 'planned', 'maintenance'];
            const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];

            logMessage(`🔄 Updating random item status to: ${randomStatus}`);
            const params = {
                action_id: 'update_' + Date.now(),
                item_id: 'item_' + Math.floor(Math.random() * 100),
                status: randomStatus
            };
            actions.execute_action('update_status', JSON.stringify(params));
        }

        function testNotification() {
            logMessage('📢 Sending notification to Python...');
            const params = {
                action_id: 'notify_' + Date.now(),
                message: 'Hello from JavaScript!',
                level: 'info'
            };
            actions.execute_action('show_notification', JSON.stringify(params));
        }

        function displayItems(items) {
            const grid = document.getElementById('itemGrid');
            grid.innerHTML = '';

            items.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'item';
                itemDiv.innerHTML = `
                    <h4>${item.name}</h4>
                    <p><strong>Type:</strong> ${item.type}</p>
                    <p><strong>Status:</strong> <span class="status ${item.status}">${item.status}</span></p>
                    <button onclick="updateItemStatus('${item.id}')">Update Status</button>
                `;
                grid.appendChild(itemDiv);
            });
        }

        function updateItemStatus(itemId) {
            const newStatus = prompt('Enter new status:', 'active');
            if (newStatus) {
                logMessage(`🔄 Updating item ${itemId} status to: ${newStatus}`);
                const params = {
                    action_id: 'update_' + Date.now(),
                    item_id: itemId,
                    status: newStatus
                };
                actions.execute_action('update_status', JSON.stringify(params));
            }
        }

        function clearLogs() {
            document.getElementById('logs').innerHTML = '';
        }

        // Wait for Qt WebChannel to be ready
        new QWebChannel(qt.webChannelTransport, function(channel) {
            // Bridge objects are available
            window.data = channel.objects.data;
            window.actions = channel.objects.actions;

            logMessage('🚀 WebChannel connected! Bridges ready.');

            // Setup signal listeners
            data.items_loaded.connect(function(itemsJson) {
                const items = JSON.parse(itemsJson);
                displayItems(items);
                logMessage(`📥 Received items update: ${items.length} items`);
            });

            data.search_results.connect(function(resultsJson) {
                const results = JSON.parse(resultsJson);
                displayItems(results);
                logMessage(`🔍 Search results: ${results.length} items found`);
            });

            actions.action_completed.connect(function(actionId, resultJson) {
                const result = JSON.parse(resultJson);
                logMessage(`✅ Action ${actionId} completed: ${JSON.stringify(result)}`);

                // Refresh data after certain actions
                if (actionId.startsWith('add_') || actionId.startsWith('update_')) {
                    setTimeout(loadAllData, 500);
                }
            });

            // Load initial data
            setTimeout(loadAllData, 100);
        });
    </script>
</body>
</html>"""

    def load_content(self):
        """Load WebView content."""
        self.webview.load_content()

    def on_items_loaded(self, items_json: str):
        """Handle items loaded signal."""
        items = json.loads(items_json)
        print(f"[SIGNAL] Items loaded: {len(items)} items")

    def on_search_results(self, results_json: str):
        """Handle search results signal."""
        results = json.loads(results_json)
        print(f"[SIGNAL] Search results: {len(results)} items")

    def on_action_completed(self, action_id: str, result_json: str):
        """Handle action completed signal."""
        result = json.loads(result_json)
        print(f"[SIGNAL] Action {action_id} completed: {result}")

    def add_random_item(self):
        """Add random item from Python side."""
        import random

        names = ["API Gateway", "Database Server", "Cache Layer", "Message Queue"]
        types = ["Service", "Database", "Cache", "Queue"]

        name = random.choice(names)
        item_type = random.choice(types)

        new_item = {
            "id": f"py_{random.randint(1000, 9999)}",
            "name": name,
            "type": item_type,
            "status": "active",
        }

        self.data_bridge.add_item(new_item)
        print(f"[PYTHON] Added item from Python: {name}")

    def update_random_status(self):
        """Update random item status from Python side."""
        items = self.data_bridge._items
        if items:
            import random

            item = random.choice(items)
            statuses = ["active", "maintenance", "updating"]
            new_status = random.choice(statuses)

            self.data_bridge.update_item(item["id"], {"status": new_status})
            print(f"[PYTHON] Updated {item['name']} status to {new_status}")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Bridge Communication Example")

    window = BridgeCommunicationWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
