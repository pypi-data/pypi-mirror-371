"""
Basic example of using the Browserness Python SDK.
"""

import os
from browserness import Browserness
from browserness.core.api_error import ApiError

# Initialize the client
# Set your API key as an environment variable named BROWSERNESS_API_KEY
api_key = os.environ.get("BROWSERNESS_API_KEY")

# If you have an API key, you can pass it in the headers
client = Browserness(api_key=api_key)

try:
    # List all browsers (will fail without valid API key)
    browsers = client.browsers.list_browsers()
    print(browsers)
except ApiError as e:
    if e.status_code == 401:
        print("Authentication failed. Please set the BROWSERNESS_API_KEY environment variable.")
        print("You can get an API key at https://browserness.com")
    else:
        print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")