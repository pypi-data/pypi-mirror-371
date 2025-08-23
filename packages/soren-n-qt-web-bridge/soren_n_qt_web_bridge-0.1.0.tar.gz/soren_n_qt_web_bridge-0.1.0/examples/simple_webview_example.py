#!/usr/bin/env python3
"""
Simple WebView Example

This example demonstrates basic usage of the qt-webview-bridge package
to create a clean WebView widget for hosting web content.
"""

import sys

try:
    from qtpy.QtCore import QTimer
    from qtpy.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    from qt_web_bridge import create_simple_webview
except ImportError as e:
    print(f"Required packages not available: {e}")
    print("Install with: pip install soren-n-qt-web-bridge[examples]")
    sys.exit(1)


class SimpleWebViewWindow(QMainWindow):
    """Simple window hosting a WebView."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple WebView Example")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create WebView using utility function
        self.webview = create_simple_webview(".")  # Load from current directory

        # Or create manually:
        # self.webview = BridgedWebView()
        # self.webview.set_web_content("./web-content")

        layout.addWidget(self.webview)

        # Set development HTML content for this example
        self.setup_example_content()

        # Load content after setup
        QTimer.singleShot(100, self.load_content)

    def setup_example_content(self):
        """Setup example HTML content."""
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple WebView Example</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
            box-sizing: border-box;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .feature {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .feature h3 {
            margin-top: 0;
            color: #fff;
        }

        .demo-button {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .demo-button:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        #status {
            margin-top: 20px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 Qt WebView Bridge</h1>

        <p style="text-align: center; font-size: 1.2em; margin-bottom: 30px;">
            Clean WebView widgets for hosting modern web UIs without styling conflicts
        </p>

        <div class="feature-grid">
            <div class="feature">
                <h3>✨ Zero Styling Conflicts</h3>
                <p>No Qt stylesheets that interfere with your web content</p>
            </div>

            <div class="feature">
                <h3>🔗 Clean Bridges</h3>
                <p>Simple Python-JavaScript communication via WebChannel</p>
            </div>

            <div class="feature">
                <h3>🚀 Easy Integration</h3>
                <p>Drop into any Qt application with minimal setup</p>
            </div>

            <div class="feature">
                <h3>🛠️ Development Friendly</h3>
                <p>Support for both dev and production content loading</p>
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <button class="demo-button" onclick="updateStatus()">
                Test JavaScript Interaction
            </button>
        </div>

        <div id="status">Ready - Click the button to test!</div>
    </div>

    <script>
        let clickCount = 0;

        function updateStatus() {
            clickCount++;
            const status = document.getElementById('status');
            status.textContent = `Button clicked ${clickCount} times! JavaScript is working perfectly.`;
            status.style.background = `hsl(${clickCount * 40}, 70%, 40%)`;

            // Log to console (visible in Qt dev tools if enabled)
            console.log(`JavaScript interaction #${clickCount}`);
        }

        // Show that the WebView loaded successfully
        document.addEventListener('DOMContentLoaded', function() {
            console.log('WebView content loaded successfully!');

            setTimeout(() => {
                const status = document.getElementById('status');
                status.textContent = 'WebView loaded successfully! JavaScript is active.';
            }, 1000);
        });
    </script>
</body>
</html>"""

        self.webview.set_dev_html_content(html_content)

    def load_content(self):
        """Load the WebView content."""
        self.webview.load_content()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Simple WebView Example")

    # Create and show window
    window = SimpleWebViewWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
