# justalock-client

[![PyPI version](https://badge.fury.io/py/justalock-client.svg)](https://badge.fury.io/py/justalock-client)
[![Python Support](https://img.shields.io/pypi/pyversions/justalock-client.svg)](https://pypi.org/project/justalock-client/)

A Python client library for the [justalock](https://justalock.dev/) distributed lock service. This library provides distributed locking functionality to coordinate work across multiple processes or services using Python's async/await patterns and context managers.

## Features

- 🔒 **Distributed Locking**: Coordinate access to shared resources across multiple processes
- 🔄 **Automatic Lock Refresh**: Keeps locks alive while your work is running
- 🎯 **Async/Await Support**: Built for modern Python with full asyncio integration
- 📦 **Zero Dependencies**: Built using only Python standard library
- 🐍 **Context Managers**: Clean resource management with `async with`

## Installation

```bash
pip install justalock-client
```

## Requirements

- Python 3.11 or higher
- No external dependencies (uses only Python standard library)

## Quick Start

```python
import asyncio
from justalock_client import Lock, generate_random_lock_id

async def main():
    # Create a lock with a unique identifier
    lock = Lock.builder(generate_random_lock_id()).build()
    
    # Use the lock as a context manager
    async with lock:
        # Your critical work here - only runs when you have the lock
        print("I have the lock! Doing important work...")
        await asyncio.sleep(1)
        print("Work completed!")

# Run the async function
asyncio.run(main())
```

## How It Works

1. **Lock Acquisition**: The context manager attempts to acquire the specified lock, retrying until successful
2. **Automatic Refresh**: The lock is automatically refreshed in the background to maintain ownership
3. **Context Management**: The `async with` statement ensures proper cleanup when exiting the block
4. **Lock Loss Detection**: If the lock is lost (due to network issues, expiration, or being stolen by another client), the lock object signals this through the `is_lock_lost` property
5. **Cleanup**: The context manager automatically stops the refresh process when exiting

### Thread Safety

- Lock instances are safe for use within a single asyncio event loop
- Do not share Lock instances across different event loops or threads
- Each async context (`async with lock:`) creates a new lock session

### Performance Notes

- Lock instances can be reused for multiple lock sessions
- The HTTP client uses connection pooling internally via urllib
- Refresh operations are performed in background tasks and don't block your code

## Usage Examples

### Basic Usage with Custom Configuration

```python
import asyncio
from justalock_client import Lock

async def process_data():
    lock = (Lock.builder("data-processing-lock")
           .client_id("worker-1")
           .lifetime_seconds(300)  # 5 minutes
           .build())
    
    async with lock:
        print("Processing data...")
        # Only one worker will process data at a time
        await simulate_data_processing()
        print("Data processing complete!")

async def simulate_data_processing():
    await asyncio.sleep(2)

asyncio.run(process_data())
```

### Monitoring Lock Status

```python
import asyncio
from justalock_client import Lock

async def monitored_work():
    lock = Lock.builder("monitored-lock").build()
    
    async with lock:
        # Start work and monitor for lock loss
        work_task = asyncio.create_task(long_running_work())
        monitor_task = asyncio.create_task(lock.wait_for_lock_lost())
        
        # Wait for either work completion or lock loss
        done, pending = await asyncio.wait(
            [work_task, monitor_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel pending tasks
        for task in pending:
            task.cancel()
        
        if work_task in done:
            print("Work completed successfully!")
            return await work_task
        else:
            print("Lock was lost, stopping work!")
            return None

async def long_running_work():
    for i in range(10):
        print(f"Working... step {i+1}/10")
        await asyncio.sleep(1)
    return "work complete"

asyncio.run(monitored_work())
```

### Service Coordination

```python
import asyncio
from justalock_client import Lock

# Service A - Database migration
async def migrate_database():
    lock = (Lock.builder("db-migration-lock")
           .client_id("migration-service")
           .lifetime_seconds(1800)  # 30 minutes
           .build())
    
    async with lock:
        print("Starting database migration...")
        await perform_migration()
        print("Migration completed!")

# Service B - Cache warming (waits for migration)
async def warm_cache():
    lock = (Lock.builder("db-migration-lock")  # Same lock ID
           .client_id("cache-service")
           .lifetime_seconds(300)
           .build())
    
    async with lock:
        print("Migration complete, warming cache...")
        await warm_application_cache()
        print("Cache warmed!")

async def perform_migration():
    # Simulate long-running migration
    await asyncio.sleep(5)

async def warm_application_cache():
    # Simulate cache warming
    await asyncio.sleep(2)

# Run services (in practice, these would be separate processes)
async def main():
    await asyncio.gather(
        migrate_database(),
        warm_cache()
    )

asyncio.run(main())
```

### Error Handling

```python
import asyncio
from justalock_client import Lock, JustalockError

async def robust_work():
    lock = Lock.builder("error-prone-work").build()
    
    try:
        async with lock:
            print("Starting work...")
            
            # Simulate work that might fail
            await risky_operation()
            print("Work completed successfully!")
            
    except JustalockError as e:
        print(f"Lock error: {e}")
    except Exception as e:
        print(f"Work failed: {e}")

async def risky_operation():
    # Simulate operation that might fail
    import random
    if random.random() < 0.3:
        raise Exception("Operation failed!")
    await asyncio.sleep(1)

asyncio.run(robust_work())
```

### Convenience Function

```python
import asyncio
from justalock_client import with_lock

async def my_work():
    print("Doing important work...")
    await asyncio.sleep(1)
    return "work result"

async def main():
    # Use the convenience function for simple cases
    result = await with_lock(
        "simple-lock",
        my_work,
        lifetime_seconds=60
    )
    print(f"Result: {result}")

asyncio.run(main())
```

### Multiple Lock ID Formats

```python
import asyncio
from justalock_client import Lock, generate_random_lock_id

async def test_lock_formats():
    # String lock IDs
    lock1 = Lock.builder("simple-string").build()
    
    # Integer lock IDs
    lock2 = Lock.builder(12345).build()
    
    # Binary lock IDs
    lock3 = Lock.builder(b"binary-lock-id").build()
    
    # UUID lock IDs
    lock4 = Lock.builder("550e8400-e29b-41d4-a716-446655440000").build()
    
    # Random lock IDs
    random_id = generate_random_lock_id()
    lock5 = Lock.builder(random_id).build()
    
    # Test all formats work
    for i, lock in enumerate([lock1, lock2, lock3, lock4, lock5], 1):
        async with lock:
            print(f"Lock {i} acquired successfully!")
            await asyncio.sleep(0.1)

asyncio.run(test_lock_formats())
```

### Periodic Tasks

```python
import asyncio
from justalock_client import Lock

async def periodic_cleanup():
    """Only one instance performs cleanup across all servers."""
    lock = (Lock.builder("daily-cleanup-lock")
           .client_id(f"cleanup-{os.getpid()}")
           .lifetime_seconds(3600)  # 1 hour max
           .build())
    
    try:
        async with lock:
            print("Starting periodic cleanup...")
            await cleanup_old_files()
            await vacuum_database()
            print("Cleanup completed!")
            return True
    except JustalockError:
        print("Another instance is performing cleanup")
        return False

async def cleanup_old_files():
    await asyncio.sleep(1)  # Simulate cleanup

async def vacuum_database():
    await asyncio.sleep(1)  # Simulate vacuum

# Schedule this to run periodically
async def main():
    while True:
        await periodic_cleanup()
        await asyncio.sleep(86400)  # Wait 24 hours

# In practice, you'd use a proper scheduler
# asyncio.run(main())
```

## API Reference

### Lock.builder(lock_id)

Creates a `LockBuilder` for configuring a lock.

**Parameters:**
- `lock_id` (str, int, or bytes): Lock identifier

**Returns:** `LockBuilder` instance

### LockBuilder Methods

#### `.client_id(client_id)`
Set a custom client identifier.
- `client_id` (str or bytes): Client identifier

#### `.lifetime_seconds(seconds)`
Set lock lifetime in seconds (1-65535).
- `seconds` (int): Lock lifetime

#### `.refresh_interval_seconds(seconds)`
Set refresh interval in seconds.
- `seconds` (float): Refresh interval

#### `.base_url(url)`
Set custom service URL (for testing or custom deployments).
- `url` (str): Service URL

#### `.build()`
Build the configured `Lock` instance.

**Returns:** `Lock` instance

### Lock Methods

#### `async with lock:`
Use the lock as an async context manager. Automatically acquires the lock on entry and releases it on exit.

#### `.is_lock_lost`
Property that returns `True` if the lock has been lost.

#### `await lock.wait_for_lock_lost()`
Wait until the lock is lost (useful for monitoring).

## Development

### Testing

The library includes comprehensive tests with a mock server:

```bash
# Run tests
python -m pytest test_justalock_client.py -v

# Or using unittest
python test_justalock_client.py
```
