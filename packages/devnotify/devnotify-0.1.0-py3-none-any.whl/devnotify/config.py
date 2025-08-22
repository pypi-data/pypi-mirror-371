import os

DEFAULT_BASE_URL = "https://api.devnotify.dev"


def get_api_key() -> str:
    key = os.getenv("DEVNOTIFY_API_KEY")
    if not key:
        raise RuntimeError(
            "DevNotify API key missing. "
            "Set it via environment variable DEVNOTIFY_API_KEY "
            "or pass explicitly to DevNotify()."
        )
    return key


def get_base_url() -> str:
    return os.getenv("DEVNOTIFY_BASE_URL", DEFAULT_BASE_URL)
