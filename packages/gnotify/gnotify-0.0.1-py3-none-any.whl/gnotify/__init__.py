"""
gnotify - A Python library for sending notifications with trading holiday awareness.
"""

from .google_spaces_notification import send_gspaces_message, get_available_channels, add_webhook
from .helpers import is_it_holiday, is_it_half_day

__version__ = "0.1.0"
__all__ = ["send_gspaces_message", "get_available_channels", "add_webhook", "is_it_holiday", "is_it_half_day"]
