from devnotify import DevNotify
from devnotify.exceptions import AuthError, RateLimitError

client = DevNotify()

try:
    client.send("Build failed", title="CI/CD", tags=["ci"])
except AuthError:
    print("Invalid API key, check your dashboard")
except RateLimitError:
    print("You hit your daily limit, upgrade your plan")
