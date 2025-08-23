# gnotify

A Python library for sending notifications to Google Spaces and Slack with trading holiday awareness.

## Installation

```bash
pip install gnotify
```

## Setup

### Environment Variables
You can create a `.env` file in your project root or set environment variables directly in your system. Or you can pass a custom configuration dictionary to the `send_gspaces_message` function.


Create a `.env` file in your project root or set environment variables for your Google Spaces webhooks:


Example `.env` file:
```env
MY_WEBHOOK=https://chat.googleapis.com/v1/spaces/YOUR_SPACE_ID/messages?key=YOUR_API_KEY&token=YOUR_TOKEN
```

**Note:** Environment variable names should follow the pattern `GSPACES_WEBHOOK_{CHANNEL_NAME}` where `CHANNEL_NAME` is uppercase.

## Usage

```python
from dotenv import load_dotenv, dotenv_values
load_dotenv(".env")  # Load environment variables from .env file

from gnotify import send_gspaces_message, is_it_holiday, get_available_channels

# Check available channels
print("Available channels:", get_available_channels())

# Send a Google Spaces message
send_gspaces_message(
    message="Hello from gnotify!",
    channel="your_channel_name",
    message_type="info"
)

# Check if it's a holiday
is_holiday = is_it_holiday("us", "20250101")  # True for New Year's Day

# Add a webhook dynamically (optional)
from gnotify import add_webhook
add_webhook("new_channel", "https://chat.googleapis.com/v1/spaces/...")

```
### Overwrite the webhook URL for an existing channel
```python

from dotenv import load_dotenv, dotenv_values
from gnotify import send_gspaces_message

config = dotenv_values(".env")  # Load environment variables from .env file

# Send an info message
send_gspaces_message(
    message="Hello from gnotify",
    channel="your_channel_name",
    message_type="info",
    webhooks=config
)

```

```python
from gnotify import send_gspaces_message

your_custom_config = {
    "your_channel_name": "https://chat.googleapis.com/v1/spaces/YOUR_SPACE_ID/messages?key=YOUR"
}

send_gspaces_message(
    message="Hello from gnotify!",
    channel="your_channel_name",
    message_type="info",
    webhooks=your_custom_config
)

```


## Features

- Google Spaces integration with environment-based webhook configuration
- Trading holiday awareness for US, EU, and JP regions
- Multiple message types (info, warning, error, success)
- Environment-based message filtering
- Secure webhook configuration via environment variables
- Dynamic webhook management

## API Reference

### send_gspaces_message

Send a message to Google Spaces channel.

**Parameters:**
- `message` (str): Message to send to channel
- `channel` (str): Name of channel (default: "emn_data_processing")
- `message_type` (str): Type of message - "warning", "error", "info", "success" (default: "error")
- `env` (str): Environment - "test" or "prod" (default: "prod")
- `region` (str): Region for holiday checking - "us", "eu", "jp" (default: "us")
- `webhooks` (dict, optional): Custom webhook URLs
- `skip_holiday_check` (bool): Skip holiday checking (default: False)

### get_available_channels

Get list of available channels from environment variables.

**Returns:**
- `list`: List of available channel names

### add_webhook

Dynamically add a webhook URL for a channel.

**Parameters:**
- `channel` (str): Channel name
- `webhook_url` (str): Webhook URL

### is_it_holiday

Check if a given date is a holiday in the specified region.

**Parameters:**
- `region` (str): The region to check for holidays ("us", "eu", "jp")
- `_in_date` (str): The date to check in format "YYYYMMDD"

**Returns:**
- `bool`: True if the date is a holiday, False otherwise

## Security

- Webhook URLs are loaded from environment variables, not hard-coded
- Use `.env` files for development and proper environment variables in production
- Never commit `.env` files to version control

## License

MIT License