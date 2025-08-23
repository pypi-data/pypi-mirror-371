"""
Bridged WebView widget for hosting TypeScript UIs with integrated Python-JavaScript bridge.

This component provides a WebView with seamless bridge functionality that:
1. Never applies Qt stylesheets that could conflict with host applications
2. Provides integrated Python-JavaScript communication via WebChannel
3. Handles development vs production web content loading
4. Is fully reusable across different projects and contexts
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from qtpy.QtCore import QObject, QUrl, Signal
from qtpy.QtWebChannel import QWebChannel
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWidgets import QVBoxLayout, QWidget


class BridgedWebView(QWidget):
    """
    Bridged WebView widget for hosting TypeScript UIs with integrated bridge functionality.

    Key Features:
    - Zero Qt styling to avoid conflicts with host applications
    - Integrated Python-JavaScript bridge via WebChannel
    - Support for both development and production web content
    - Fully reusable across projects
    - Minimal API surface focused on bridging

    Usage:
        webview = BridgedWebView()
        webview.set_web_content("path/to/dist", dev_html="dev.html")
        webview.register_bridge_object("api", my_bridge_object)
        webview.load_content()
    """

    # Signals for lifecycle events
    content_loaded = Signal()
    content_failed = Signal(str)  # error message
    bridge_ready = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # State
        self._web_content_path: Path | None = None
        self._dev_html_path: Path | None = None
        self._dev_html_content: str | None = None
        self._bridge_objects: dict[str, QObject] = {}
        self._load_callbacks: list[Callable[[], None]] = []

        # Setup UI with zero styling
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the WebView with minimal, non-conflicting layout."""
        # Create layout with zero margins to be completely transparent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create WebEngineView with no custom styling
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Setup WebChannel for Python-JavaScript communication
        self.web_channel = QWebChannel()
        self.web_view.page().setWebChannel(self.web_channel)

        # Connect load signals
        self.web_view.loadFinished.connect(self._on_load_finished)

    def set_web_content(self, content_path: str, dev_html: str | None = None) -> None:
        """
        Set the path to web content.

        Args:
            content_path: Path to built web content (e.g., "dist" directory)
            dev_html: Optional path to development HTML file relative to content_path
        """
        self._web_content_path = Path(content_path)
        if dev_html:
            self._dev_html_path = self._web_content_path / dev_html

    def set_dev_html_content(self, html_content: str) -> None:
        """
        Set development HTML content directly (for embedded UIs).

        Args:
            html_content: Complete HTML content as string
        """
        self._dev_html_content = html_content

    def register_bridge_object(self, name: str, obj: QObject) -> None:
        """
        Register a Python object to be accessible from JavaScript.

        Args:
            name: JavaScript object name
            obj: Python QObject with @Slot methods for JS to call
        """
        self._bridge_objects[name] = obj
        self.web_channel.registerObject(name, obj)

    def add_load_callback(self, callback: Callable[[], None]) -> None:
        """
        Add a callback to be called when content is loaded.

        Args:
            callback: Function to call when content loads successfully
        """
        self._load_callbacks.append(callback)

    def load_content(self) -> None:
        """
        Load the web content based on configured paths.

        Loading Priority:
        1. Production build (content_path/index.html)
        2. Development HTML file (dev_html_path)
        3. Development HTML content (dev_html_content)
        """
        try:
            # Try production build first
            if self._web_content_path:
                index_html = self._web_content_path / "index.html"
                if index_html.exists():
                    self._load_file(index_html)
                    return

            # Try development HTML file
            if self._dev_html_path and self._dev_html_path.exists():
                self._load_file(self._dev_html_path)
                return

            # Use development HTML content
            if self._dev_html_content:
                self._load_html_content(self._dev_html_content)
                return

            # No content available
            raise FileNotFoundError("No web content available to load")

        except Exception as e:
            self.content_failed.emit(str(e))

    def _load_file(self, file_path: Path) -> None:
        """Load HTML file."""
        url = QUrl.fromLocalFile(str(file_path.absolute()))
        self.web_view.load(url)

    def _load_html_content(self, html_content: str) -> None:
        """Load HTML content directly."""
        # Create temporary file for development
        temp_dir = Path(__file__).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        temp_file = temp_dir / "webview_content.html"

        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        self._load_file(temp_file)

    def _on_load_finished(self, success: bool) -> None:
        """Handle WebView load completion."""
        if success:
            self.content_loaded.emit()
            self.bridge_ready.emit()

            # Call registered callbacks
            for callback in self._load_callbacks:
                try:
                    callback()
                except Exception as e:
                    print(f"WebView load callback error: {e}")
        else:
            self.content_failed.emit("WebView failed to load content")

    def execute_javascript(
        self, script: str, callback: Callable[[Any], None] | None = None
    ) -> None:
        """
        Execute JavaScript in the WebView.

        Args:
            script: JavaScript code to execute
            callback: Optional callback for the result
        """
        page = self.web_view.page()
        if callback:
            page.runJavaScript(script, callback)
        else:
            page.runJavaScript(script)

    def get_bridge_object(self, name: str) -> QObject | None:
        """Get registered bridge object by name."""
        return self._bridge_objects.get(name)

    def clear_bridge_objects(self) -> None:
        """Clear all registered bridge objects."""
        self._bridge_objects.clear()
        # Note: WebChannel objects persist until page reload

    def reload_content(self) -> None:
        """Reload the current web content."""
        self.web_view.reload()

    def set_zoom_factor(self, factor: float) -> None:
        """Set WebView zoom factor (1.0 = 100%)."""
        self.web_view.setZoomFactor(factor)

    def get_url(self) -> str:
        """Get current WebView URL."""
        try:
            url = self.web_view.url()
            return str(url.toString()) if url else ""
        except Exception:
            return ""

    def set_user_agent(self, user_agent: str) -> None:
        """Set custom user agent string."""
        self.web_view.page().profile().setHttpUserAgent(user_agent)

    def enable_dev_tools(self, enable: bool = True) -> None:
        """Enable or disable developer tools (F12)."""
        # Note: This requires WebEngineSettings attribute for dev tools
        # Implementation depends on Qt version and availability
        # settings = self.web_view.page().settings()
        pass

    def get_web_engine_view(self) -> QWebEngineView:
        """Get the underlying QWebEngineView for advanced usage."""
        return self.web_view

    def get_web_channel(self) -> QWebChannel:
        """Get the WebChannel for direct manipulation."""
        return self.web_channel
