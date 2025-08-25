"""
Qt WebView Bridge - Clean WebView widgets for hosting modern web UIs.

This package provides Qt WebView components designed to host TypeScript/React/Vue UIs
without Qt styling conflicts, with clean Python-JavaScript bridges and minimal overhead.

Key Features:
- Zero Qt styling conflicts with host applications
- Clean Python-JavaScript communication via WebChannel
- Support for development and production content loading
- Modular bridge system for different use cases
- QtPy compatibility for cross-platform Qt support
- Minimal API surface for easy integration

Basic Usage:
    from qt_web_bridge import BridgedWebView, WebViewBridge

    # Create webview widget
    webview = BridgedWebView()
    webview.set_web_content("path/to/web/dist")

    # Setup Python-JavaScript bridge
    bridge = WebViewBridge()
    webview.register_bridge_object("api", bridge)

    # Load content
    webview.load_content()

Advanced Usage:
    from qt_web_bridge import DataBridge, ActionBridge, WebViewPanel

    # Create specialized bridges
    data_bridge = DataBridge()
    action_bridge = ActionBridge()

    # Use with panel wrapper
    panel = WebViewPanel("My Web UI")
    webview = panel.setup_webview("path/to/content")
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .bridge import ActionBridge, DataBridge, WebViewBridge
from .panel import WebViewPanel
from .utils import create_simple_webview, detect_qt_styling_conflicts
from .webview import BridgedWebView

__all__ = [
    # Core components
    "BridgedWebView",
    "WebViewBridge",
    "DataBridge",
    "ActionBridge",
    "WebViewPanel",
    # Utilities
    "create_simple_webview",
    "detect_qt_styling_conflicts",
    # Package info
    "__version__",
    "__author__",
    "__email__",
]
