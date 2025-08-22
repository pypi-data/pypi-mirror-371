class DevNotifyError(Exception):
    """Base SDK error."""


class AuthError(DevNotifyError):
    """401 unauthorized / bad key."""


class RateLimitError(DevNotifyError):
    """429 rate limit exceeded."""


class ServerError(DevNotifyError):
    """5xx from server after retries."""


class NetworkError(DevNotifyError):
    """Transport errors: timeouts, DNS, connection issues."""
