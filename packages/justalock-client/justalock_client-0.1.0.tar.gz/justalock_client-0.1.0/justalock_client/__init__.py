"""
justalock-client - A distributed lock client for the justalock service

This library provides a simple distributed lock backed by the justalock service.
The core functionality allows you to hold a lock in order to perform work while the lock is held.

The library uses Python's context managers and asyncio for clean resource management
and non-blocking operations.

Example:
    import asyncio
    from justalock_client import Lock, generate_random_lock_id

    async def main():
        lock = Lock.builder(generate_random_lock_id()).build()

        async with lock:
            # Your work here - only runs when you have the lock
            await asyncio.sleep(1)
            print("Work completed!")

    asyncio.run(main())
"""

import asyncio
import base64
import hashlib
import secrets
import time
import urllib.error
import urllib.request
from typing import Any, Optional, Union, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor

__version__ = "0.1.0"
__all__ = ["Lock", "LockBuilder", "JustalockError", "generate_random_lock_id", "with_lock"]

DEFAULT_LIFETIME_SECONDS = 60
DEFAULT_BASE_URL = "https://justalock.dev/"
DEFAULT_REFRESH_INTERVAL_RATIO = 2.5


class JustalockError(Exception):
    """Errors that can occur during locking operations."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def generate_random_lock_id() -> bytes:
    """
    Generate a cryptographically random 16-byte lock ID.

    Creates a lock identifier that can be used with the Lock class.
    The generated ID includes a timestamp component to help ensure uniqueness.

    Returns:
        bytes: Random lock ID (exactly 16 bytes)
    """
    timestamp = int(time.time()).to_bytes(8, "big")
    random_bytes = secrets.token_bytes(8)
    return timestamp + random_bytes


def normalize_lock_id(lock_id: Union[str, int, bytes]) -> bytes:
    """
    Convert various lock ID formats to a standardized 16-byte format.

    Supports multiple input formats:
    - str: UUID (with/without hyphens), hex (32 chars), base64 (22/24 chars), ASCII (16 chars)
    - int: Converted to big-endian bytes (must be >= 0)
    - bytes: Must be exactly 16 bytes

    Args:
        lock_id: The lock identifier in any supported format

    Returns:
        bytes: Normalized 16-byte lock ID

    Raises:
        ValueError: If the input format is invalid or unsupported
    """
    if isinstance(lock_id, str):
        # Handle UUID format (with or without hyphens)
        if len(lock_id) == 36 and "-" in lock_id:
            hex_str = lock_id.replace("-", "")
            return bytes.fromhex(hex_str)
        if len(lock_id) == 32 and all(c in "0123456789abcdefABCDEF" for c in lock_id):
            return bytes.fromhex(lock_id)
        # Handle base64 format
        if len(lock_id) in (22, 24):
            try:
                return base64.b64decode(lock_id + "==")[:16]
            except (ValueError, TypeError):
                pass
        # Handle ASCII strings (16 bytes exactly)
        if len(lock_id) == 16:
            return lock_id.encode("utf-8")
        # Hash strings of any other length to 16 bytes
        return hashlib.sha256(lock_id.encode("utf-8")).digest()[:16]

    if isinstance(lock_id, int):
        if lock_id < 0:
            raise ValueError(f"Lock ID must be non-negative, got {lock_id}")
        # Convert to 16-byte big-endian format
        return lock_id.to_bytes(16, "big")

    if isinstance(lock_id, bytes):
        if len(lock_id) == 16:
            return lock_id
        if len(lock_id) < 16:
            # Pad with zeros
            return lock_id + b"\x00" * (16 - len(lock_id))
        # Hash to 16 bytes
        return hashlib.sha256(lock_id).digest()[:16]

    raise ValueError(f"Unsupported lock ID type: {type(lock_id)}")


def normalize_client_id(client_id: Optional[Union[str, bytes]]) -> bytes:
    """
    Convert various client ID formats to bytes.

    If no client ID is provided, generates a random one automatically.

    Args:
        client_id: The client identifier (optional)

    Returns:
        bytes: Client ID as bytes

    Raises:
        ValueError: If the input type is unsupported
    """
    if client_id is None:
        # Generate random client ID
        timestamp = int(time.time()).to_bytes(8, "big")
        random_bytes = secrets.token_bytes(20)
        return timestamp + random_bytes

    if isinstance(client_id, str):
        return client_id.encode("utf-8")

    if isinstance(client_id, bytes):
        return client_id

    raise ValueError(f"Unsupported client ID type: {type(client_id)}")


class HTTPClient:
    """Simple HTTP client using urllib for making requests to the justalock service."""

    def __init__(self, timeout: float = 2.0) -> None:
        self.timeout = timeout

    async def post(self, url: str, data: bytes) -> tuple[int, bytes]:
        """
        Make an HTTP POST request.

        Args:
            url: Request URL
            data: Request body data

        Returns:
            tuple[int, bytes]: Status code and response body

        Raises:
            JustalockError: If there's a network error or timeout
        """

        def _make_request() -> tuple[int, bytes]:
            try:
                request = urllib.request.Request(
                    url,
                    data=data,
                    headers={
                        "Content-Type": "application/octet-stream",
                        "Content-Length": str(len(data)),
                    },
                    method="POST",
                )

                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return response.status, response.read()

            except urllib.error.HTTPError as e:
                return e.code, e.read()
            except (urllib.error.URLError, OSError) as e:
                raise JustalockError(f"Network error: {e}") from e
            except Exception as e:
                raise JustalockError(f"Request failed: {e}") from e

        # Run the blocking operation in a thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                return await loop.run_in_executor(executor, _make_request)
            except Exception as e:
                if isinstance(e, JustalockError):
                    raise
                raise JustalockError(f"Request failed: {e}") from e


class LockBuilder:
    """Builder for creating Lock instances with custom configuration."""

    def __init__(self, lock_id: Union[str, int, bytes]) -> None:
        """
        Initialize a LockBuilder with the given lock ID.

        Args:
            lock_id: The lock identifier in any supported format
        """
        self._lock_id = normalize_lock_id(lock_id)
        self._client_id: Optional[Union[str, bytes]] = None
        self._lifetime_seconds: Optional[int] = None
        self._refresh_interval_seconds: Optional[float] = None
        self._base_url: Optional[str] = None

    def client_id(self, client_id: Union[str, bytes]) -> "LockBuilder":
        """
        Set a custom client ID to uniquely identify this client.

        It is recommended that you set this value to use the same Client ID
        across restarts of the same client. If you do not, then a restart
        will prevent the client from grabbing the lock until the lock expires.

        Args:
            client_id: Client identifier (max 64 bytes recommended)

        Returns:
            LockBuilder: Self for method chaining
        """
        self._client_id = client_id
        return self

    def lifetime_seconds(self, seconds: int) -> "LockBuilder":
        """
        Set how long the lock will stay locked before expiring.

        Refreshing the lock will extend the lifetime by this amount.

        Args:
            seconds: Lifetime in seconds (1-65535)

        Returns:
            LockBuilder: Self for method chaining

        Raises:
            ValueError: If seconds is not in valid range
        """
        if not isinstance(seconds, int) or seconds < 1 or seconds > 65535:
            raise ValueError("Lifetime must be an integer between 1 and 65535 seconds")
        self._lifetime_seconds = seconds
        return self

    def refresh_interval_seconds(self, seconds: float) -> "LockBuilder":
        """
        Set how often to refresh the lock.

        Args:
            seconds: Refresh interval in seconds

        Returns:
            LockBuilder: Self for method chaining

        Raises:
            ValueError: If seconds is not positive
        """
        if seconds <= 0:
            raise ValueError("Refresh interval must be positive")
        self._refresh_interval_seconds = seconds
        return self

    def base_url(self, url: str) -> "LockBuilder":
        """
        Set a custom URL for the justalock service.

        The lock builder uses the real justalock service by default, but this
        can be overridden for testing or custom deployments.

        Args:
            url: Custom service URL

        Returns:
            LockBuilder: Self for method chaining
        """
        self._base_url = url
        return self

    def build(self) -> "Lock":
        """
        Build the Lock instance with the configured options.

        Returns:
            Lock: Configured lock instance
        """
        client_id = normalize_client_id(self._client_id)
        lifetime_seconds = self._lifetime_seconds or DEFAULT_LIFETIME_SECONDS
        refresh_interval_seconds = (
            self._refresh_interval_seconds
            or lifetime_seconds / DEFAULT_REFRESH_INTERVAL_RATIO
        )
        base_url = self._base_url or DEFAULT_BASE_URL

        # Build the lock URL
        lock_id_str = (
            base64.urlsafe_b64encode(self._lock_id).decode("ascii").rstrip("=")
        )
        if not base_url.endswith("/"):
            base_url += "/"

        lock_url = f"{base_url}{lock_id_str}?s={lifetime_seconds}"

        return Lock(
            lock_id=self._lock_id,
            client_id=client_id,
            lifetime_seconds=lifetime_seconds,
            refresh_interval_seconds=refresh_interval_seconds,
            url=lock_url,
            http_client=HTTPClient(),
        )


class Lock:
    """
    A distributed lock client.

    Lock instances provide exclusive access to a shared resource across multiple
    processes or services. The lock is automatically refreshed while in use and
    can be used as a context manager for clean resource management.
    """

    def __init__(
        self,
        lock_id: bytes,
        client_id: bytes,
        lifetime_seconds: int,
        refresh_interval_seconds: float,
        url: str,
        http_client: HTTPClient,
    ) -> None:
        self._lock_id = lock_id
        self._client_id = client_id
        self._lifetime_seconds = lifetime_seconds
        self._refresh_interval_seconds = refresh_interval_seconds
        self._url = url
        self._http_client = http_client
        self._refresh_task: Optional[asyncio.Task] = None
        self._lock_lost_event = asyncio.Event()

    @classmethod
    def builder(cls, lock_id: Union[str, int, bytes]) -> LockBuilder:
        """
        Create a LockBuilder for configuring a Lock.

        Args:
            lock_id: The lock identifier in any supported format

        Returns:
            LockBuilder: Builder for configuring the lock
        """
        return LockBuilder(lock_id)

    @property
    def lock_id(self) -> str:
        """Get the lock ID as a string."""
        return base64.urlsafe_b64encode(self._lock_id).decode("ascii").rstrip("=")

    @property
    def client_id(self) -> str:
        """Get the client ID as a string."""
        return base64.urlsafe_b64encode(self._client_id).decode("ascii").rstrip("=")

    @property
    def lifetime_seconds(self) -> int:
        """Get the lock lifetime in seconds."""
        return self._lifetime_seconds

    async def try_lock(self) -> bool:
        """
        Attempt to acquire the lock once.

        Returns:
            bool: True if lock was acquired, False if already held by another client

        Raises:
            JustalockError: If there was an error communicating with the service
        """
        try:
            status_code, body = await self._http_client.post(self._url, self._client_id)

            if status_code == 200:
                return True
            if status_code == 409:
                return False
            if 400 <= status_code < 500:
                error_msg = (
                    body.decode("utf-8", errors="ignore")
                    if body
                    else f"Client error: {status_code}"
                )
                raise JustalockError(error_msg)
            raise JustalockError(f"Server error: {status_code}")

        except JustalockError:
            raise
        except Exception as e:
            raise JustalockError(f"Request failed: {e}") from e

    async def _refresh_loop(self) -> None:
        """Background task to keep the lock refreshed."""
        last_lock_time = time.time()

        while not self._lock_lost_event.is_set():
            try:
                # Wait for the refresh interval
                await asyncio.wait_for(
                    self._lock_lost_event.wait(), timeout=self._refresh_interval_seconds
                )
                # Event was set, exit the loop
                break
            except asyncio.TimeoutError:
                # Time to refresh the lock
                pass

            now = time.time()
            time_since_last_lock = now - last_lock_time

            # If we're close to expiration, give up
            if time_since_last_lock >= (self._lifetime_seconds - 1):
                self._lock_lost_event.set()
                break

            try:
                acquired = await self.try_lock()
                if acquired:
                    last_lock_time = now
                else:
                    # Lost the lock
                    self._lock_lost_event.set()
                    break
            except JustalockError:
                # Network or service error, continue trying
                pass

    async def __aenter__(self) -> "Lock":
        """
        Async context manager entry.

        Acquires the lock and starts the refresh process.

        Returns:
            Lock: Self

        Raises:
            JustalockError: If the lock could not be acquired
        """
        # Keep trying to acquire the lock with timeout
        timeout = 15.0  # 15 second timeout to handle lock expiry
        start_time = time.time()
        while True:
            try:
                acquired = await self.try_lock()
                if acquired:
                    break
                # Check timeout
                if time.time() - start_time > timeout:
                    raise JustalockError("Timeout waiting to acquire lock")
                # Wait a bit before retrying
                await asyncio.sleep(0.1)
            except Exception as e:
                if isinstance(e, JustalockError):
                    raise
                raise JustalockError(f"Failed to acquire lock: {e}") from e

        # Start the refresh task
        self._lock_lost_event.clear()
        self._refresh_task = asyncio.create_task(self._refresh_loop())

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit.

        Stops the refresh process and releases the lock.
        """
        # Signal the refresh task to stop
        self._lock_lost_event.set()

        # Wait for the refresh task to complete
        if self._refresh_task:
            try:
                await asyncio.wait_for(self._refresh_task, timeout=1.0)
            except asyncio.TimeoutError:
                self._refresh_task.cancel()
                try:
                    await self._refresh_task
                except asyncio.CancelledError:
                    pass
            self._refresh_task = None

    @property
    def is_lock_lost(self) -> bool:
        """
        Check if the lock has been lost.

        Returns:
            bool: True if the lock has been lost
        """
        return self._lock_lost_event.is_set()

    async def wait_for_lock_lost(self) -> None:
        """
        Wait until the lock is lost.

        This can be useful for monitoring the lock status during long-running operations.
        """
        await self._lock_lost_event.wait()

    def __str__(self) -> str:
        """String representation of the lock."""
        return (f"Lock(lockId={self.lock_id}, clientId={self.client_id}, "
                f"lifetime={self._lifetime_seconds}s)")

    def __repr__(self) -> str:
        """Detailed string representation of the lock."""
        return (
            f"Lock(lock_id={self.lock_id!r}, client_id={self.client_id!r}, "
            f"lifetime_seconds={self._lifetime_seconds}, url={self._url!r})"
        )


# Convenience function for common usage patterns
async def with_lock(
    lock_id: Union[str, int, bytes],
    work_func: Callable[[], Awaitable[Any]],
    *,
    client_id: Optional[Union[str, bytes]] = None,
    lifetime_seconds: Optional[int] = None,
    base_url: Optional[str] = None,
) -> Any:
    """
    Execute an async function while holding a distributed lock.

    This is a convenience function that handles lock creation, acquisition,
    and cleanup automatically.

    Args:
        lock_id: The lock identifier
        work_func: Async function to execute while holding the lock
        client_id: Optional client identifier
        lifetime_seconds: Optional lock lifetime in seconds
        base_url: Optional custom service URL

    Returns:
        Any: The result of work_func

    Raises:
        JustalockError: If there was an error with the lock

    Example:
        async def my_work():
            await asyncio.sleep(1)
            return "done"

        result = await with_lock("8cf9c504-9299-49d0-8224-6537673a4429", my_work, lifetime_seconds=30)
    """
    builder = Lock.builder(lock_id)

    if client_id is not None:
        builder = builder.client_id(client_id)
    if lifetime_seconds is not None:
        builder = builder.lifetime_seconds(lifetime_seconds)
    if base_url is not None:
        builder = builder.base_url(base_url)

    lock = builder.build()

    async with lock:
        return await work_func()
