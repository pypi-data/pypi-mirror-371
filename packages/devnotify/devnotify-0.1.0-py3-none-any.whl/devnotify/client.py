from __future__ import annotations

import json
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import requests

import devnotify

from .config import get_api_key, get_base_url
from .exceptions import (
    AuthError,
    DevNotifyError,
    NetworkError,
    RateLimitError,
    ServerError,
)


@dataclass
class DevNotify:
    """
    Python SDK client for DevNotify.

    Example:
        ```python
        import devnotify

        devnotify.api_key = "devk_123"   # global
        client = devnotify.DevNotify()

        # OR
        client = devnotify.DevNotify(api_key="devk_123")

        client.send("Hello from DevNotify")
        ```
    """

    api_key: str | None = None
    timeout: float = 5.0
    retries: int = 1
    backoff: float = 0.5

    def __post_init__(self):
        if not self.api_key:
            if devnotify.api_key:
                self.api_key = devnotify.api_key
            else:
                self.api_key = get_api_key()

        self.__base_url = get_base_url()

    def send(
        self,
        message: str,
        title: str | None = None,
        priority: str = "normal",  # "low" | "normal" | "high"
        tags: Iterable[str] | None = None,
        silent: bool = False,
    ) -> dict[str, Any]:
        """
        Send a notification to DevNotify.

        Args:
            message (str): The main notification message.
            title (str, optional): Title to display in app/push.
            tags (list[str], optional): Tags for filtering in the app.
            priority (str, optional): One of "low", "normal", "high".
            silent (bool, optional): If True, no push sound.

        Returns:
            dict: API response. Usually includes "status" and notification id.

        Raises:
            AuthError: Invalid/missing API key.
            RateLimitError: Exceeded allowed quota.
            ServerError: DevNotify backend issue (5xx).
            NetworkError: Connection/timeout problem.
            DevNotifyError: Other client-side validation.
        """
        if not message or not isinstance(message, str):
            raise ValueError("message must be a non-empty string")

        if priority not in {"low", "normal", "high"}:
            raise ValueError("priority must be one of: low, normal, high")

        payload = {
            "message": message,
            "title": title,
            "priority": priority,
            "tags": list(tags) if tags else None,
            "silent": bool(silent),
        }

        url = f"{self.__base_url.rstrip('/')}/notification/create"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        attempt = 0
        while True:
            try:
                r = requests.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=self.timeout,
                )
            except requests.RequestException as e:
                if attempt < self.retries:
                    attempt += 1
                    time.sleep(self.backoff * attempt)
                    continue
                raise NetworkError(str(e)) from e

            if r.status_code == 200:
                try:
                    return r.json()
                except ValueError:
                    return {"status": "ok", "raw": r.text}

            if r.status_code == 401:
                raise AuthError(r.text or "Unauthorized")

            if r.status_code == 429:
                raise RateLimitError(r.text or "Rate limit exceeded")

            if 500 <= r.status_code < 600:
                if attempt < self.retries:
                    attempt += 1
                    time.sleep(self.backoff * attempt)
                    continue
                raise ServerError(r.text or f"Server error {r.status_code}")

            # 4xx other than 401/429
            raise DevNotifyError(f"{r.status_code}: {r.text}")
