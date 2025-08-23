"""
Test the BridgedWebView component.
"""

import sys
from pathlib import Path

import pytest

try:
    from qtpy.QtWidgets import QApplication

    HAS_QT = True
except ImportError:
    HAS_QT = False

from qt_web_bridge import BridgedWebView


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    if not HAS_QT:
        pytest.skip("Qt not available")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


def test_bridged_webview_creation(qapp):
    """Test that BridgedWebView can be created without errors."""
    webview = BridgedWebView()
    assert webview is not None
    assert hasattr(webview, "web_view")
    assert hasattr(webview, "web_channel")


def test_zero_styling(qapp):
    """Test that BridgedWebView has no Qt styling applied."""
    webview = BridgedWebView()

    # Check widget has no stylesheet
    assert not webview.styleSheet()

    # Check layout has zero margins
    layout = webview.layout()
    margins = layout.getContentsMargins()
    assert margins == (0, 0, 0, 0)
    assert layout.spacing() == 0


def test_web_content_configuration():
    """Test web content path configuration."""
    webview = BridgedWebView()

    # Test setting web content path
    webview.set_web_content("test/path", "dev.html")
    assert webview._web_content_path == Path("test/path")
    assert webview._dev_html_path == Path("test/path/dev.html")


def test_dev_html_content():
    """Test development HTML content setting."""
    webview = BridgedWebView()

    test_html = "<html><body>Test</body></html>"
    webview.set_dev_html_content(test_html)
    assert webview._dev_html_content == test_html


def test_bridge_object_registration(qapp):
    """Test bridge object registration."""
    from qtpy.QtCore import QObject

    webview = BridgedWebView()
    bridge_obj = QObject()

    webview.register_bridge_object("test", bridge_obj)
    assert "test" in webview._bridge_objects
    assert webview.get_bridge_object("test") is bridge_obj


def test_load_callbacks():
    """Test load callback registration."""
    webview = BridgedWebView()

    callback_called = []

    def test_callback():
        callback_called.append(True)

    webview.add_load_callback(test_callback)
    assert len(webview._load_callbacks) == 1


def test_javascript_execution(qapp):
    """Test JavaScript execution interface."""
    webview = BridgedWebView()

    # Should not raise an error (even though no content is loaded)
    webview.execute_javascript("console.log('test')")


def test_utility_methods(qapp):
    """Test various utility methods."""
    webview = BridgedWebView()

    # Test zoom factor
    webview.set_zoom_factor(1.5)

    # Test URL getting (should return empty initially)
    url = webview.get_url()
    assert isinstance(url, str)

    # Test clear bridge objects
    webview.clear_bridge_objects()
    assert len(webview._bridge_objects) == 0
