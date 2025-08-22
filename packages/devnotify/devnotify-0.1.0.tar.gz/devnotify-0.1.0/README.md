# DevNotify (Python SDK)

[![QA (CI)](https://github.com/linustg/devnotify-python/actions/workflows/qa.yml/badge.svg)](https://github.com/linustg/devnotify-python/actions/workflows/qa.yml)

Send push notifications from your code via DevNotify.

## What is DevNotify?

When you’re building SaaS apps or backend services, important events happen all the time — a new user signs up, a payment fails, an error pops up. But most teams either miss them or rely on clunky email alerts or overkill monitoring setups.

DevNotify gives you a lightweight way to get real-time notifications straight to your phone, with almost no setup. It’s made for developers who want fast feedback without wiring up a full alerting system.

## Installation

```bash
pip install devnotify
```

## Quickstart

```python
import devnotify

devnotify.api_key = "your_api_key_here"

from devnotify import DevNotify

client = DevNotify()
client.send("New user signed up!", title="Signup", tags=["users"])
```

## Why DevNotify?

- **Instant alerts:** Get notified on your phone as soon as something important happens.
- **Easy integration:** Add a few lines of simple code and get started quickly.
- **Flexible:** Send notifications from any Python script, backend, or automation.
- **Organized:** Use tags and titles to group and filter your notifications.
- **Free tier:** Start for free with a generous usage limit which should be enough for most small projects.

## Links

- [DevNotify Documentation](https://devnotify.com/docs)
- [PyPi](https://pypi.org/project/devnotify/)

## Configuration

To configure DevNotify, simply set your API key. You get the API key on the web dashboard [here](https://devnotify.com/dashboard)

```python
import devnotify

devnotify.api_key = "your_api_key_here"
```

Or set the `DEVNOTIFY_API_KEY` environment variable in your system.

```bash
export DEVNOTIFY_API_KEY="your_api_key_here"
```

on Linux or macOS, or set it in your system environment variables on Windows.

## Advanced usage

### Custom retries

You can customize the retry behavior of the DevNotify client by specifying the `retries` and `backoff` parameters.
The backoff parameter controls the delay between retries.

```python
client = DevNotify(retries=5, backoff=1.0)
```

### Silent notifications

You can send notifications without getting a push notification on your phone by setting `silent=True`.
The notifications will still be logged and visible in the DevNotify app.

```python
client = DevNotify(silent=True)
```

## Examples

### Basic notification sending

```python
import devnotify
from devnotify import DevNotify

# Quickstart: set your API key
devnotify.api_key = "your_api_key_here"

client = DevNotify()
client.send("Hello from DevNotify!", title="Quickstart")
```

### With Tags

```python
import devnotify
from devnotify import DevNotify

devnotify.api_key = "your_api_key_here"

client = DevNotify()
client.send(
    "New user signed up",
    title="Signup Event",
    tags=["users", "signup"]
)
```

### Error Handling

```python
import devnotify
from devnotify import DevNotify
from devnotify.exceptions import AuthError, RateLimitError, DevNotifyError

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
```

### Retry Configuration

```python
import devnotify
from devnotify import DevNotify

devnotify.api_key = "your_api_key_here"

# Customize retries and backoff (default: retries=3, backoff=0.5s)
client = DevNotify(retries=5, backoff=1.0)

client.send("Background sync complete", silent=True)
```

### Error Handling

```python
import devnotify
from devnotify import DevNotify
from devnotify.exceptions import AuthError, RateLimitError, DevNotifyError

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
except ServerError as e:
    print(f"Server error occurred: {e}")
except NetworkError as e:
    print(f"Network error occurred: {e}")
```
