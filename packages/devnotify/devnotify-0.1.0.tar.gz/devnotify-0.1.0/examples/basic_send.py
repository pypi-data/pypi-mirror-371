import devnotify
from devnotify import DevNotify

# Quickstart: set your API key
devnotify.api_key = "your_api_key_here"

client = DevNotify()
client.send("Hello from DevNotify!", title="Quickstart")
