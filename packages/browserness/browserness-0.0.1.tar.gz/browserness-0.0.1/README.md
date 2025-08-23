# Browserness Python SDK

The official Python SDK for the Browserness API, allowing you to programmatically create and manage remote browser instances.

## Installation

```bash
pip install browserness
```

Or if you're installing from source:

```bash
pip install .
```

## Quick Start

```python
from browserness import Browserness

# Initialize the client
client = Browserness()

# List all browsers
browsers = client.list_browsers()
print(browsers)

# Create a new browser
browser = client.create_browser()
print(browser)
```

## Async Support

The SDK also includes an async client:

```python
import asyncio
from browserness import AsyncBrowserness

async def main():
    # Initialize the async client
    client = AsyncBrowserness()
    
    # List all browsers
    browsers = await client.list_browsers()
    print(browsers)

asyncio.run(main())
```

## Documentation

For detailed documentation, please refer to the [API documentation](https://api.browserness.com/docs).

## License

This SDK is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.