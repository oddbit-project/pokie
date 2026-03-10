import logging
import signal
from rick.mixin import Injectable
from rick.base import Di

logger = logging.getLogger(__name__)


class SignalManager(Injectable):
    def __init__(self, di: Di):
        super().__init__(di)
        self.handlers = {}

    def add_handler(self, signalnum: int, handler: callable):
        if not callable(handler):
            raise TypeError("add_handler(): handler must be callable")
        if not isinstance(signalnum, int):
            raise TypeError("add_handler(): signalnum must be an integer")

        if signalnum in self.handlers:
            self.handlers[signalnum].append(handler)
        else:
            self.handlers[signalnum] = [handler]
            self._register_handler(signalnum)

    def _register_handler(self, signalnum: int):
        def wrap_signal(signal_no, stack_frame):
            for handler in self.handlers[signal_no]:
                try:
                    handler(self.get_di(), signal_no, stack_frame)
                except Exception as e:
                    logger.exception("Signal handler %s failed: %s", handler, e)

        signal.signal(signalnum, wrap_signal)
