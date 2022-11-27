# Adding signal handlers

```python
import signal


def signal_handler(di, signalnum, stack_trace):
    pass

# get signal manager
mgr = di.get(DI_SIGNAL) # type: pokie.core.SignalManager

# register custom handler
mgr.add_handler(signal.SIGINT, signal_handler())

```