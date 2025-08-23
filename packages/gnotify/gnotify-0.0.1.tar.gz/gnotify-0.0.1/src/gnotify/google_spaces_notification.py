import os
from datetime import datetime
from json import dumps
from typing import Dict, Optional


from httplib2 import Http
from loguru import logger
from pytz import timezone

from .helpers import is_it_holiday


def _load_webhooks_from_env() -> Dict[str, str]:
    """
    Load webhook URLs from environment variables.
    Environment variables should be named: {CHANNEL_NAME}

    Returns:
        Dict[str, str]: Dictionary mapping channel names to webhook URLs
    """
    webhooks = {}

    # Get all environment variables
    for key, value in os.environ.items():
        webhooks[key] = value

    return webhooks

# Load webhooks from environment variables
DEFAULT_GSPACES_WEBHOOKS = _load_webhooks_from_env()

MESSAGE_TYPE = {
    "warning": "*[WARNING]*",
    "error": "*[ERROR]*",
    "info": "*[INFO]*",
    "success": "*[SUCCESS]*",
}

REGION_TIMEZONE = {
    "us": "US/Eastern",
    "eu": "Europe/London",
    "jp": "Asia/Tokyo"
}


def send_gspaces_message(
    message: str,
    channel: str = "emn_data_processing",
    message_type: str = "error",
    env: str = "prod",
    region: str = "us",
    webhooks: Optional[Dict[str, str]] = None,
    skip_holiday_check: bool = False
) -> None:
    """
    Send a message to Google Spaces channel.

    Args:
        message (str): message to send to channel
        channel (str): name of channel, default is "emn_data_processing"
        message_type (str): "warning", "error", "info", "success", default is "error"
        env (str): "test" or "prod", default is "prod", whether to send notification or not
        region (str): "us", "eu", "jp", default is "us", for holiday checking
        webhooks (dict, optional): custom webhook URLs to override defaults
        skip_holiday_check (bool): skip holiday checking, default is False

    Returns: None

    Environment Variables:
        GSPACES_WEBHOOK_{CHANNEL_NAME}: Webhook URL for the channel (uppercase channel name)
        Example: GSPACES_WEBHOOK_EMN_DATA_PROCESSING=https://chat.googleapis.com/...
    """
    if env == "test":
        logger.info("Test environment - message not sent")
        return

    if message is None:
        logger.error("message cannot be None!")
        return

    # Use provided webhooks or default ones from environment
    webhook_config = webhooks or DEFAULT_GSPACES_WEBHOOKS
    webhook_url = webhook_config.get(channel)

    if webhook_url is None:
        available_channels = list(webhook_config.keys())
        logger.error(f"No webhook URL found for channel: {channel}. Available channels: {available_channels}")
        logger.error(f"Make sure to set environment variable: {channel.upper()}")
        return

    # Holiday check
    if not skip_holiday_check:
        region_tz = timezone(REGION_TIMEZONE.get(region, "US/Eastern"))
        today = datetime.now(region_tz).strftime("%Y%m%d")

        logger.info(f"Check if it is holiday in {region} region on {today}")
        is_holiday = is_it_holiday(region=region, _in_date=today)

        if is_holiday:
            logger.info("It is holiday, do not send message")
            return

    # Send message
    try:
        http_obj = Http()
        message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
        bot_message = {'text': f'{MESSAGE_TYPE.get(message_type, "*[WARNING]*")} {message}'}

        response = http_obj.request(
            uri=webhook_url,
            method='POST',
            headers=message_headers,
            body=dumps(bot_message),
        )

        logger.info(f"Response status: {response[0].get('status')}")

    except Exception as e:
        logger.error(f"Failed to send message to Google Spaces: {str(e)}")


def get_available_channels() -> list:
    """
    Get list of available channels from environment variables.

    Returns:
        list: List of available channel names
    """
    return list(DEFAULT_GSPACES_WEBHOOKS.keys())


def add_webhook(channel: str, webhook_url: str) -> None:
    """
    Dynamically add a webhook URL for a channel.

    Args:
        channel (str): Channel name
        webhook_url (str): Webhook URL
    """
    DEFAULT_GSPACES_WEBHOOKS[channel] = webhook_url
    logger.info(f"Added webhook for channel: {channel}")


if __name__ == '__main__':
    # Print available channels for debugging
    print("Available channels:", get_available_channels())

    send_gspaces_message(
        message="This message belong to google space channel",
        channel="emn_data_processing",
        message_type="info"
    )
