# Skope SDK

A Python SDK for interacting with the Skope API.

## Installation

```bash
pip install skope-sdk
```

## Usage

```python
from skope import Skope, Event

# Initialize the client
client = Skope(
    api_key="your_api_key_here",
    base_url="https://api.useskope.com"  # Optional, defaults to production
)

# Create events for billing
events = [
    Event(
        user_id="customer_123",
        unit="api_calls",
        value=100
    ),
    Event(
        user_id="customer_456", 
        unit="storage_gb",
        value=5
    )
]

# Upload events in batch
result = client.upload_events(events)
print(f"Upload result: {result}")
```

## Error Handling

The SDK will raise HTTP exceptions if API requests fail:

```python
import requests

try:
    result = client.upload_events(events)
except requests.exceptions.HTTPError as e:
    print(f"Failed to upload events: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## API Reference

### SkopeClient

#### `__init__(api_key: str, base_url: str = "https://api.useskope.com")`

Initialize a new Skope client.

- `api_key`: Your Skope API key
- `base_url`: The base URL of the Skope API (optional)

#### `upload_events(events: List[Event]) -> Dict[str, Any]`

Upload multiple events for billing in one request.

- `events`: A list of Event objects
- Returns: The response data containing upload status

### Event

A Pydantic model representing a billing event.

#### Fields:

- `user_id`: str (required) - The customer identifier
- `unit`: str (required) - The billing unit name
- `value`: int (optional) - The value to aggregate over
