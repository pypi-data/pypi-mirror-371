# Soren-N Qt Web Bridge

[![PyPI version](https://badge.fury.io/py/soren-n-qt-web-bridge.svg)](https://badge.fury.io/py/soren-n-qt-web-bridge)
[![Python versions](https://img.shields.io/pypi/pyversions/soren-n-qt-web-bridge.svg)](https://pypi.org/project/soren-n-qt-web-bridge/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Clean Qt WebView widgets for hosting modern web UIs without styling conflicts. Features robust automated CI/CD with comprehensive multi-backend testing and fully automated PyPI publishing.

## ✨ Features

- **🎨 Zero Qt Styling Conflicts** - No interference with your web content's CSS
- **🔗 Clean Python-JavaScript Bridges** - Simple bidirectional communication via WebChannel
- **🚀 Easy Integration** - Drop into any Qt application with minimal setup
- **🛠️ Development Friendly** - Support for both development and production content loading
- **📦 QtPy Compatible** - Works with PySide6, PyQt6, PySide2, and PyQt5
- **🎯 Minimal API** - Small, focused API surface for easy learning

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install soren-n-qt-web-bridge

# For examples and development
pip install soren-n-qt-web-bridge[examples]
```

### Basic Usage

```python
from qtpy.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from qt_web_bridge import BridgedWebView

app = QApplication([])

# Create main window
window = QMainWindow()
central_widget = QWidget()
window.setCentralWidget(central_widget)
layout = QVBoxLayout(central_widget)

# Create and setup WebView
webview = BridgedWebView()
webview.set_web_content("path/to/your/web/dist")
layout.addWidget(webview)

# Load content
webview.load_content()

window.show()
app.exec()
```

### With Python-JavaScript Bridge

```python
from qt_web_bridge import BridgedWebView, DataBridge, ActionBridge

# Create WebView
webview = BridgedWebView()
webview.set_web_content("web-content")

# Create bridges
data_bridge = DataBridge()
action_bridge = ActionBridge()

# Set up data
items = [
    {"id": "1", "name": "Item 1", "description": "First item"},
    {"id": "2", "name": "Item 2", "description": "Second item"}
]
data_bridge.set_items(items)

# Register action handler
def handle_button_click(params):
    print(f"Button clicked with params: {params}")
    return {"status": "success", "message": "Button click handled"}

action_bridge.register_action_handler("button_click", handle_button_click)

# Register bridges with WebView
webview.register_bridge_object("data", data_bridge)
webview.register_bridge_object("actions", action_bridge)

# Load content
webview.load_content()
```

### JavaScript Side

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Web UI</title>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
</head>
<body>
    <div id="app">Loading...</div>
    
    <script>
        new QWebChannel(qt.webChannelTransport, function(channel) {
            // Access Python bridges
            const data = channel.objects.data;
            const actions = channel.objects.actions;
            
            // Get data from Python
            const itemsJson = data.get_all_items();
            const items = JSON.parse(itemsJson);
            console.log('Items from Python:', items);
            
            // Call Python action
            function handleClick() {
                actions.execute_action('button_click', JSON.stringify({
                    button: 'test',
                    timestamp: Date.now()
                }));
            }
            
            // Listen for data updates from Python
            data.items_loaded.connect(function(itemsJson) {
                const items = JSON.parse(itemsJson);
                updateUI(items);
            });
        });
    </script>
</body>
</html>
```

## 🔧 Core Components

### `BridgedWebView`
Main WebView widget with zero Qt styling interference.

### `WebViewBridge`
Base class for Python-JavaScript communication.

### `DataBridge` 
Specialized bridge for data synchronization.

### `ActionBridge`
Specialized bridge for handling user actions.

### `WebViewPanel`
Optional panel wrapper for host application integration.

## 🎯 Use Cases

- **Houdini Plugin UIs** - Integrate React/Vue UIs into Houdini panels
- **Maya Tools** - Modern web UIs without Qt styling conflicts  
- **Desktop Applications** - Hybrid Qt/Web applications
- **Data Visualization** - Interactive charts and dashboards

## 🔍 Examples

Run the included examples:

```bash
# Simple WebView demo
python examples/simple_webview_example.py

# Bridge communication demo  
python examples/bridge_communication_example.py
```

## 📄 License

GPL v3 or later - see [LICENSE](LICENSE) file for details.
