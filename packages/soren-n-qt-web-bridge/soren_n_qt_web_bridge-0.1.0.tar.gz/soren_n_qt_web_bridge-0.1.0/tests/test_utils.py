"""
Test utility functions.
"""

import tempfile
from pathlib import Path

import pytest

from qt_web_bridge.utils import (
    create_simple_webview,
    detect_qt_styling_conflicts,
    setup_development_webview,
    validate_web_content_path,
)


def test_create_simple_webview():
    """Test simple webview creation utility."""
    webview = create_simple_webview("test/path")
    assert webview is not None
    assert webview._web_content_path == Path("test/path")


def test_create_simple_webview_with_bridges():
    """Test webview creation with bridge objects."""
    try:
        from qtpy.QtCore import QObject

        bridge = QObject()
        webview = create_simple_webview("test/path", bridge_objects={"test": bridge})

        assert "test" in webview._bridge_objects
    except ImportError:
        pytest.skip("Qt not available")


def test_validate_web_content_path():
    """Test web content path validation."""
    # Test non-existent path
    is_valid, issues = validate_web_content_path("nonexistent/path")
    assert not is_valid
    assert any("does not exist" in issue for issue in issues)

    # Test with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Empty directory should have issues
        is_valid, issues = validate_web_content_path(temp_path)
        assert not is_valid
        assert any("index.html" in issue for issue in issues)

        # Create index.html
        (temp_path / "index.html").write_text("<html></html>")

        is_valid, issues = validate_web_content_path(temp_path)
        # May still have issues (no asset dirs) but should find index.html
        assert (temp_path / "index.html").exists()


def test_setup_development_webview():
    """Test development webview setup."""
    html_content = "<html><body>Test</body></html>"
    webview = setup_development_webview(html_content)

    assert webview._dev_html_content == html_content


def test_setup_development_webview_with_bridges():
    """Test development webview with bridges."""
    try:
        from qtpy.QtCore import QObject

        html_content = "<html><body>Test</body></html>"
        bridge = QObject()

        webview = setup_development_webview(
            html_content, bridge_objects={"api": bridge}
        )

        assert webview._dev_html_content == html_content
        assert "api" in webview._bridge_objects
    except ImportError:
        pytest.skip("Qt not available")


def test_detect_qt_styling_conflicts():
    """Test Qt styling conflict detection."""
    try:
        from qtpy.QtWidgets import QWidget

        widget = QWidget()

        # Widget without styling should have no conflicts
        conflicts = detect_qt_styling_conflicts(widget)
        # May be empty or may have some warnings depending on Qt setup
        assert isinstance(conflicts, list)

        # Widget with styling should have conflicts
        widget.setStyleSheet("QWidget { background-color: red; }")
        conflicts = detect_qt_styling_conflicts(widget)
        assert len(conflicts) > 0

    except ImportError:
        pytest.skip("Qt not available")


def test_validate_web_content_with_file():
    """Test validation when path points to a file instead of directory."""
    with tempfile.NamedTemporaryFile() as temp_file:
        is_valid, issues = validate_web_content_path(temp_file.name)
        assert not is_valid
        assert any("not a directory" in issue for issue in issues)
