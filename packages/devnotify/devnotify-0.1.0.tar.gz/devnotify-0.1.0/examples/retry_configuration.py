import devnotify
from devnotify import DevNotify

devnotify.api_key = "your_api_key_here"

# Customize retries and backoff (default: retries=3, backoff=0.5s)
client = DevNotify(retries=5, backoff=1.0)

client.send("Background sync complete", silent=True)
