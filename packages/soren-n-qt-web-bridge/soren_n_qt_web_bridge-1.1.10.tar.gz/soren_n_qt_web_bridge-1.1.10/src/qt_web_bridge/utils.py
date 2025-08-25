"""
Utility functions for WebView setup and debugging.

This module provides helper functions for common WebView tasks,
debugging, and integration with various Qt applications.
"""

import warnings
from collections.abc import Callable
from pathlib import Path
from typing import Any

from qtpy.QtCore import QObject
from qtpy.QtWidgets import QWidget

from .bridge import ActionBridge, DataBridge, WebViewBridge
from .webview import BridgedWebView


def create_simple_webview(
    content_path: str,
    bridge_objects: dict[str, QObject] | None = None,
    parent: QWidget | None = None,
) -> BridgedWebView:
    """
    Create a simple WebView with optional bridge objects.

    Args:
        content_path: Path to web content directory
        bridge_objects: Optional dict of name -> bridge object mappings
        parent: Optional parent widget

    Returns:
        Configured BridgedWebView ready to load content

    Example:
        # Simple usage
        webview = create_simple_webview("./web-dist")
        webview.load_content()

        # With bridge objects
        bridge = WebViewBridge()
        webview = create_simple_webview(
            "./web-dist",
            bridge_objects={"api": bridge}
        )
        webview.load_content()
    """
    webview = BridgedWebView(parent)
    webview.set_web_content(content_path)

    if bridge_objects:
        for name, obj in bridge_objects.items():
            webview.register_bridge_object(name, obj)

    return webview


def create_data_webview(
    content_path: str, initial_data: list[dict[str, Any]] | None = None
) -> tuple[BridgedWebView, DataBridge]:
    """
    Create a WebView with a pre-configured DataBridge.

    Args:
        content_path: Path to web content
        initial_data: Optional initial data items

    Returns:
        Tuple of (webview, data_bridge)

    Example:
        items = [{"id": "1", "name": "Item 1"}]
        webview, bridge = create_data_webview("./dist", items)
        webview.load_content()
    """
    webview = BridgedWebView()
    webview.set_web_content(content_path)

    data_bridge = DataBridge()
    if initial_data:
        data_bridge.set_items(initial_data)

    webview.register_bridge_object("data", data_bridge)

    return webview, data_bridge


def create_action_webview(
    content_path: str,
    action_handlers: dict[str, Callable[[dict[str, Any]], Any]] | None = None,
) -> tuple[BridgedWebView, ActionBridge]:
    """
    Create a WebView with a pre-configured ActionBridge.

    Args:
        content_path: Path to web content
        action_handlers: Optional dict of action_type -> handler mappings

    Returns:
        Tuple of (webview, action_bridge)

    Example:
        def handle_download(params):
            return {"status": "downloaded", "file": params["file"]}

        handlers = {"download": handle_download}
        webview, bridge = create_action_webview("./dist", handlers)
        webview.load_content()
    """
    webview = BridgedWebView()
    webview.set_web_content(content_path)

    action_bridge = ActionBridge()
    if action_handlers:
        for action_type, handler in action_handlers.items():
            action_bridge.register_action_handler(action_type, handler)

    webview.register_bridge_object("actions", action_bridge)

    return webview, action_bridge


def detect_qt_styling_conflicts(widget: QWidget) -> list[str]:
    """
    Detect potential Qt styling conflicts that could interfere with WebView content.

    Args:
        widget: Widget to check (typically a parent container)

    Returns:
        List of warning messages about potential conflicts

    Example:
        warnings = detect_qt_styling_conflicts(my_main_window)
        for warning in warnings:
            print(f"Warning: {warning}")
    """
    warnings_list = []

    # Check for custom stylesheets that might affect WebViews
    if hasattr(widget, "styleSheet") and widget.styleSheet():
        stylesheet = widget.styleSheet()

        # Check for global selectors that could affect WebViews
        if "QWidget" in stylesheet:
            warnings_list.append(
                "Global QWidget stylesheet detected - may conflict with WebView styling"
            )

        if "background-color" in stylesheet.lower():
            warnings_list.append(
                "Background color styles detected - may conflict with WebView content"
            )

        if "font" in stylesheet.lower():
            warnings_list.append(
                "Font styles detected - may conflict with WebView typography"
            )

    # Check parent chain for problematic styling
    parent = widget.parent()
    depth = 0
    while parent and depth < 10:  # Avoid infinite loops
        if hasattr(parent, "styleSheet") and parent.styleSheet():
            warnings_list.append(f"Parent widget at depth {depth} has custom styling")
        parent = parent.parent()
        depth += 1

    return warnings_list


def validate_web_content_path(content_path: str | Path) -> tuple[bool, list[str]]:
    """
    Validate that a web content path is properly structured.

    Args:
        content_path: Path to web content directory

    Returns:
        Tuple of (is_valid, list_of_issues)

    Example:
        is_valid, issues = validate_web_content_path("./web-dist")
        if not is_valid:
            for issue in issues:
                print(f"Issue: {issue}")
    """
    path = Path(content_path)
    issues = []

    if not path.exists():
        issues.append(f"Content path does not exist: {path}")
        return False, issues

    if not path.is_dir():
        issues.append(f"Content path is not a directory: {path}")
        return False, issues

    # Check for index.html (production build)
    index_html = path / "index.html"
    if not index_html.exists():
        issues.append("No index.html found (production build missing)")

    # Check for common web assets
    common_assets = ["js", "css", "assets", "static"]
    found_assets = []
    for asset_dir in common_assets:
        if (path / asset_dir).exists():
            found_assets.append(asset_dir)

    if not found_assets:
        issues.append("No common web asset directories found (js, css, assets, static)")

    # Check for very large directories (potential issues)
    try:
        file_count = len(list(path.rglob("*")))
        if file_count > 10000:
            issues.append(
                f"Very large number of files ({file_count}) - may cause performance issues"
            )
    except (OSError, PermissionError):
        issues.append("Could not enumerate files in content directory")

    is_valid = len(issues) == 0
    return is_valid, issues


def setup_development_webview(
    html_content: str, bridge_objects: dict[str, QObject] | None = None
) -> BridgedWebView:
    """
    Setup a WebView for development with inline HTML content.

    Args:
        html_content: HTML content as string
        bridge_objects: Optional bridge objects

    Returns:
        Configured BridgedWebView ready to load

    Example:
        html = '''<!DOCTYPE html>
        <html><body><h1>Test UI</h1></body></html>'''

        webview = setup_development_webview(html, {"api": my_bridge})
        webview.load_content()
    """
    webview = BridgedWebView()
    webview.set_dev_html_content(html_content)

    if bridge_objects:
        for name, obj in bridge_objects.items():
            webview.register_bridge_object(name, obj)

    return webview


def warn_about_styling_conflicts(widget: QWidget) -> None:
    """
    Emit warnings about potential Qt styling conflicts.

    Args:
        widget: Widget to check

    Example:
        # Check for conflicts before adding WebView
        warn_about_styling_conflicts(main_window)
        webview = BridgedWebView(main_window)
    """
    conflicts = detect_qt_styling_conflicts(widget)

    for conflict in conflicts:
        warnings.warn(
            f"Potential WebView styling conflict: {conflict}", UserWarning, stacklevel=2
        )


def create_debug_webview(content_path: str) -> BridgedWebView:
    """
    Create a WebView with debug logging enabled.

    Args:
        content_path: Path to web content

    Returns:
        WebView with debug bridge attached

    Example:
        webview = create_debug_webview("./web-dist")
        webview.load_content()  # Will log debug info
    """
    webview = BridgedWebView()
    webview.set_web_content(content_path)

    # Create debug bridge
    debug_bridge = WebViewBridge()

    def debug_callback() -> None:
        print(f"[DEBUG] WebView loaded: {webview.get_url()}")

    webview.add_load_callback(debug_callback)
    webview.register_bridge_object("debug", debug_bridge)

    return webview
