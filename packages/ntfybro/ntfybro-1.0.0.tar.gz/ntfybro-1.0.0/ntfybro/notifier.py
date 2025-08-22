import requests
from typing import Optional, Dict, Any
import logging

class NtfyNotifier:
    """
    Universal Ntfy notification class for sending notifications across projects.
    
    This class provides a reusable interface for sending notifications via ntfy.sh service.
    It can be easily integrated into any project and configured with different settings.
    """
    
    def __init__(self, 
                 server_url: str = "https://ntfy.example.com",
                 default_topic: str = "local",
                 default_email: Optional[str] = None,
                 default_icon: Optional[str] = None):
        """
        Initialize the NtfyNotifier.
        
        Args:
            server_url: The ntfy server URL (default: https://ntfy.example.com)
            default_topic: Default topic/channel name
            default_email: Default email for notifications
            default_icon: Default icon URL for notifications
        """
        self.server_url = server_url.rstrip('/')
        self.default_topic = default_topic
        self.default_email = default_email
        self.default_icon = default_icon
        self.logger = logging.getLogger(__name__)
    
    def send_notification(self,
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
                         actions: Optional[str] = None) -> bool:
        """
        Send a notification via ntfy.
        
        Args:
            message: The notification message
            title: Notification title
            topic: Topic/channel name (uses default if not provided)
            priority: Priority level (1=min, 3=default, 5=max)
            tags: Comma-separated tags (e.g., "warning,skull")
            email: Email address for email notifications
            icon: Icon URL for the notification
            click_url: URL to open when notification is clicked
            attach_url: URL of file to attach
            delay: Delay delivery (e.g., "30min", "9am")
            actions: JSON string of action buttons
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        try:
            # Use provided topic or default
            topic_to_use = topic or self.default_topic
            url = f"{self.server_url}/{topic_to_use}"
            
            # Build headers
            headers = {"Content-Type": "text/plain; charset=utf-8"}
            
            if title:
                headers["Title"] = title
            if priority != 3:  # Only set if different from default
                headers["Priority"] = str(priority)
            if tags:
                headers["Tags"] = tags
            if email or self.default_email:
                headers["Email"] = email or self.default_email
            if icon or self.default_icon:
                headers["Icon"] = icon or self.default_icon
            if click_url:
                headers["Click"] = click_url
            if attach_url:
                headers["Attach"] = attach_url
            if delay:
                headers["Delay"] = delay
            if actions:
                headers["Actions"] = actions
            
            # Send the notification
            response = requests.post(url, data=message.encode('utf-8'), headers=headers, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Notification sent successfully to topic '{topic_to_use}'")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending notification: {e}")
            return False
    
    def send_simple(self, message: str, title: str = "Notification") -> bool:
        """
        Send a simple notification with just message and title.
        
        Args:
            message: The notification message
            title: The notification title
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        return self.send_notification(message=message, title=title)
    
    def send_error(self, message: str, title: str = "Error") -> bool:
        """
        Send an error notification with high priority and error styling.
        
        Args:
            message: The error message
            title: The error title
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        return self.send_notification(
            message=message,
            title=title,
            priority=5,
            tags="rotating_light,skull"
        )
    
    def send_warning(self, message: str, title: str = "Warning") -> bool:
        """
        Send a warning notification with medium-high priority.
        
        Args:
            message: The warning message
            title: The warning title
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        return self.send_notification(
            message=message,
            title=title,
            priority=4,
            tags="warning"
        )
    
    def send_success(self, message: str, title: str = "Success") -> bool:
        """
        Send a success notification with positive styling.
        
        Args:
            message: The success message
            title: The success title
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        return self.send_notification(
            message=message,
            title=title,
            tags="white_check_mark"
        )