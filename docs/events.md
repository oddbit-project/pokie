# Events

Pokie includes an event system for decoupled communication between modules. Events are dispatched by name and handled
by registered handlers, with support for priority-based execution ordering.

## Event Registration

Events are registered in a module's `events` dictionary. The structure maps event names to priority levels, and each
priority level contains a list of handler class paths:

```python
from pokie.core import BaseModule


class Module(BaseModule):
    name = "my_module"
    description = "My module"

    events = {
        "afterLogin": {
            10: ["my_module.event.LoginLogger"],
        },
        "afterOrderCreate": {
            10: ["my_module.event.SendConfirmationEmail"],
            20: ["my_module.event.UpdateInventory"],
        },
    }
```

Lower priority numbers execute first. Handlers within the same priority level are executed in list order.

## Event Handlers

There are two types of event handlers: class-based and function-based.

### Class-Based Handlers

Class-based handlers extend `EventHandler` from Rick and define a method with the same name as the event:

```python
from rick.event import EventHandler


class LoginLogger(EventHandler):

    def afterLogin(self, **kwargs):
        user = kwargs.get("user")
        print(f"User logged in: {user.get_id()}")
```

The handler class is instantiated with the DI container on each dispatch. The event method receives the keyword
arguments passed to `dispatch()`.

### Function-Based Handlers

Function-based handlers are simple callables that receive `event_name` as an additional keyword argument:

```python
def on_login(event_name, **kwargs):
    user = kwargs.get("user")
    print(f"Event {event_name}: user {user.get_id()}")
```

## Dispatching Events

Events are dispatched via the `EventManager`, accessible through the DI container:

```python
from pokie.constants import DI_EVENTS

evt_mgr = di.get(DI_EVENTS)
evt_mgr.dispatch(di, "afterLogin", user=user)
```

### dispatch(di, event_name, **kwargs) -> bool

Dispatches an event by name. Returns `True` if the event was dispatched (handlers exist), `False` if no handlers are
registered for the event.

Handlers are executed synchronously in priority order. If an event has no registered handlers, the dispatch is a no-op.

**Circular dependency protection:** If a handler dispatches the same event that is currently being processed, a
`RuntimeError` is raised.

## EventManager API

| Method | Description |
|--------|-------------|
| `add_handler(event_name, handler, priority=100)` | Register a handler (dotted class path string) |
| `remove_handler(event_name, handler)` | Remove a handler. Returns `True` if found. |
| `get_events()` | List all registered event names |
| `dispatch(di, event_name, **kwargs)` | Dispatch an event |
| `purge()` | Remove all events and handlers |
| `load_handlers(src)` | Load handlers from a config dict (used during module loading) |
