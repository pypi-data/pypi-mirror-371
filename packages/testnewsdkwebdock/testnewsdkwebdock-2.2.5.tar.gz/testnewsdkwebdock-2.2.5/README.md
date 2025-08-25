# Webdock Python SDK

A Python SDK for interacting with the Webdock API.

## Installation

```bash
pip install webdock-python-sdk
```

## Usage

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from webdock import Webdock

# Initialize the SDK with your API token
webdock = Webdock("your-api-token-here")

# Use the SDK to interact with different resources
servers = webdock.servers
account = webdock.account
# ... and more
```

## Available Resources

- `webdock.servers` - Manage servers
- `webdock.account` - Account information
- `webdock.images` - Server images
- `webdock.profiles` - Server profiles
- `webdock.events` - Events
- `webdock.hooks` - Webhooks
- `webdock.locations` - Server locations
- `webdock.scripts` - Scripts
- `webdock.shellUsers` - Shell users
- `webdock.sshkeys` - SSH keys
- `webdock.snapshots` - Snapshots
- `webdock.operation` - Operations
