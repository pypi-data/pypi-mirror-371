"""
Optional panel wrapper for integrating WebView components into host applications.

This provides host-specific integration while maintaining clean separation
between the core WebView functionality and application-specific features.
"""

from qtpy.QtWidgets import QVBoxLayout, QWidget

from .webview import BridgedWebView


class WebViewPanel(QWidget):
    """
    Panel wrapper for WebView components.

    This class provides:
    - Integration with host application panel systems
    - Optional title bars and controls
    - Clean lifecycle management
    - Zero styling conflicts with host UI

    Usage:
        panel = WebViewPanel("My Web UI")
        webview = panel.setup_webview("path/to/web/content")
        panel.load_webview_content()
    """

    def __init__(self, title: str = "WebView Panel", parent: QWidget | None = None):
        super().__init__(parent)

        self.title = title
        self.webview: BridgedWebView | None = None

        # Setup with zero styling to avoid host conflicts
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup panel layout with zero styling."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Panel will contain webview when created

    def setup_webview(
        self, content_path: str, dev_html: str | None = None
    ) -> BridgedWebView:
        """
        Create and setup the WebView component.

        Args:
            content_path: Path to web content
            dev_html: Optional development HTML file

        Returns:
            The created WebView instance
        """
        if self.webview:
            # Remove existing webview
            layout = self.layout()
            if layout is not None:
                layout.removeWidget(self.webview)
            self.webview.setParent(None)

        # Create new webview
        self.webview = BridgedWebView(self)
        self.webview.set_web_content(content_path, dev_html)

        # Add to layout
        layout = self.layout()
        if layout is not None:
            layout.addWidget(self.webview)

        return self.webview

    def load_webview_content(self) -> None:
        """Load content in the WebView."""
        if self.webview:
            self.webview.load_content()
        else:
            raise RuntimeError("WebView not setup. Call setup_webview() first.")

    def get_webview(self) -> BridgedWebView | None:
        """Get the WebView instance."""
        return self.webview

    def set_title(self, title: str) -> None:
        """Set panel title (for host integration)."""
        self.title = title

    def get_title(self) -> str:
        """Get panel title."""
        return self.title

    def cleanup(self) -> None:
        """Clean up resources when panel is closed."""
        if self.webview:
            self.webview.clear_bridge_objects()

    def reload_content(self) -> None:
        """Reload webview content."""
        if self.webview:
            self.webview.reload_content()

    def set_zoom_factor(self, factor: float) -> None:
        """Set webview zoom factor."""
        if self.webview:
            self.webview.set_zoom_factor(factor)

    def execute_javascript(self, script: str) -> None:
        """Execute JavaScript in the webview."""
        if self.webview:
            self.webview.execute_javascript(script)


# Utility functions for common panel configurations
def create_asset_browser_panel() -> WebViewPanel:
    """
    Create a WebView panel configured for asset browsing.

    Returns:
        Configured WebViewPanel ready for asset browser content
    """
    return WebViewPanel("Asset Browser")


def create_ai_assistant_panel() -> WebViewPanel:
    """
    Create a WebView panel configured for AI assistant.

    Returns:
        Configured WebViewPanel ready for AI assistant content
    """
    return WebViewPanel("AI Assistant")


def create_dashboard_panel() -> WebViewPanel:
    """
    Create a WebView panel configured for dashboards.

    Returns:
        Configured WebViewPanel ready for dashboard content
    """
    return WebViewPanel("Dashboard")


def create_generic_webview_panel(title: str, content_path: str) -> WebViewPanel:
    """
    Create a generic WebView panel for any TypeScript UI.

    Args:
        title: Panel title
        content_path: Path to web content

    Returns:
        Ready-to-use WebViewPanel
    """
    panel = WebViewPanel(title)
    panel.setup_webview(content_path)
    panel.load_webview_content()

    return panel
