# ntfybro

A simple and reusable Python package for sending notifications via [ntfy.sh](https://ntfy.sh) service.

## Features

- 🚀 Easy to use and integrate into any Python project
- 📱 Support for all ntfy.sh features (priority, tags, icons, attachments, etc.)
- 🎯 Pre-configured notification types (error, warning, success)
- 🔧 Configurable server URL and default settings
- 📝 Comprehensive logging support
- 🐍 Type hints for better development experience

## Installation

```bash
pip install ntfybro
```

## Quick Start

```python
from ntfybro import NtfyNotifier

# Initialize the notifier
notifier = NtfyNotifier(
    server_url="https://ntfy.sh",  # Optional, defaults to https://ntfy.hvacvoice.com
    default_topic="my-app",        # Your topic/channel name
    default_email="user@example.com"  # Optional default email
)

# Send a simple notification
notifier.send_simple("Hello World!", "My App")

# Send different types of notifications
notifier.send_success("Task completed successfully!")
notifier.send_warning("This is a warning message")
notifier.send_error("Something went wrong!")
```

## Advanced Usage

### Custom Notifications

```python
# Send a notification with all available options
notifier.send_notification(
    message="Deployment completed",
    title="Production Deploy",
    topic="deployments",
    priority=4,  # 1=min, 3=default, 5=max
    tags="rocket,checkered_flag",
    email="admin@company.com",
    icon="https://example.com/icon.png",
    click_url="https://dashboard.company.com",
    attach_url="https://example.com/report.pdf",
    delay="30min",  # Delay delivery
    actions='[{"action": "view", "label": "View Dashboard", "url": "https://dashboard.company.com"}]'
)
```

### Configuration Options

```python
notifier = NtfyNotifier(
    server_url="https://your-ntfy-server.com",  # Custom server
    default_topic="my-project",                 # Default topic
    default_email="notifications@company.com",  # Default email
    default_icon="https://company.com/logo.png" # Default icon
)
```

## API Reference

### NtfyNotifier Class

#### Constructor

```python
NtfyNotifier(
    server_url: str = "https://ntfy.example.com",
    default_topic: str = "local",
    default_email: Optional[str] = None,
    default_icon: Optional[str] = None
)
```

#### Methods

##### send_notification()

Send a custom notification with full control over all parameters.

```python
send_notification(
    message: str,
    title: Optional[str] = None,
    topic: Optional[str] = None,
    priority: int = 3,
    tags: Optional[str] = None,
    email: Optional[str] = None,
    icon: Optional[str] = None,
    click_url: Optional[str] = None,
    attach_url: Optional[str] = None,
    delay: Optional[str] = None,
    actions: Optional[str] = None
) -> bool
```

##### send_simple()

Send a simple notification with just message and title.

```python
send_simple(message: str, title: str = "Notification") -> bool
```

##### send_error()

Send an error notification with high priority and error styling.

```python
send_error(message: str, title: str = "Error") -> bool
```

##### send_warning()

Send a warning notification with medium-high priority.

```python
send_warning(message: str, title: str = "Warning") -> bool
```

##### send_success()

Send a success notification with positive styling.

```python
send_success(message: str, title: str = "Success") -> bool
```

## Examples

### Integration with Web Applications

```python
from ntfybro import NtfyNotifier
from flask import Flask

app = Flask(__name__)
notifier = NtfyNotifier(default_topic="webapp-alerts")

@app.route('/deploy')
def deploy():
    try:
        # Your deployment logic here
        notifier.send_success("Deployment completed successfully!")
        return "Deployed!"
    except Exception as e:
        notifier.send_error(f"Deployment failed: {str(e)}")
        return "Deployment failed", 500
```

### Monitoring Scripts

```python
from ntfybro import NtfyNotifier
import psutil

notifier = NtfyNotifier(default_topic="server-monitoring")

# Check system resources
cpu_usage = psutil.cpu_percent()
if cpu_usage > 80:
    notifier.send_warning(
        f"High CPU usage detected: {cpu_usage}%",
        "Server Alert"
    )
```

## Requirements

- Python 3.7+
- requests >= 2.25.0

## License

MIT License

Copyright (c) 2025 https://brodev.uz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support and questions, please visit [https://brodev.uz](https://brodev.uz)