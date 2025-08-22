import devnotify
from devnotify import DevNotify
from devnotify.exceptions import AuthError, DevNotifyError, RateLimitError

devnotify.api_key = "your_api_key_here"
client = DevNotify()

try:
    client.send("Build failed", title="CI/CD")
except AuthError:
    print("Invalid API key — check your dashboard.")
except RateLimitError:
    print("Daily notification limit exceeded.")
except DevNotifyError as e:
    print(f"Unexpected DevNotify error: {e}")
