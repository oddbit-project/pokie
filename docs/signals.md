# Signal Handlers

Pokie provides a `SignalManager` for registering OS signal handlers (e.g. SIGINT, SIGTERM) through the DI container.
Multiple handlers can be registered for the same signal, and they are executed in registration order.

## SignalManager

The signal manager is available in the DI container as `DI_SIGNAL`:

```python
from pokie.constants import DI_SIGNAL

mgr = di.get(DI_SIGNAL)
```

### add_handler(signalnum, handler)

Register a handler for a specific signal number.

```python
import signal
from pokie.constants import DI_SIGNAL


def on_shutdown(di, signal_no, stack_frame):
    print(f"Received signal {signal_no}, shutting down...")
    # cleanup resources


mgr = di.get(DI_SIGNAL)
mgr.add_handler(signal.SIGINT, on_shutdown)
mgr.add_handler(signal.SIGTERM, on_shutdown)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `signalnum` | int | OS signal number (e.g. `signal.SIGINT`) |
| `handler` | callable | Handler function |

**Handler signature:**

```python
def handler(di: Di, signal_no: int, stack_frame) -> None
```

| Parameter | Description |
|-----------|-------------|
| `di` | The DI container |
| `signal_no` | The signal number that was received |
| `stack_frame` | The current stack frame |

**Raises:**

- `TypeError` if `signalnum` is not an integer
- `TypeError` if `handler` is not callable

## Multiple Handlers

Multiple handlers can be registered for the same signal. They are executed in registration order:

```python
def handler_one(di, signal_no, stack_frame):
    print("First handler")

def handler_two(di, signal_no, stack_frame):
    print("Second handler")

mgr.add_handler(signal.SIGINT, handler_one)
mgr.add_handler(signal.SIGINT, handler_two)
# Both handlers run when SIGINT is received
```

## Error Handling

If a handler raises an exception, the error is logged and execution continues to the next handler. This ensures that
one failing handler does not prevent other handlers from running.
