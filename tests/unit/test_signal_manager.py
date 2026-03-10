import signal
from unittest.mock import patch

import pytest
from rick.base import Di

from pokie.core.signal_manager import SignalManager


class TestSignalManager:
    def test_init_empty_handlers(self):
        di = Di()
        mgr = SignalManager(di)
        assert mgr.handlers == {}

    def test_add_handler_new_signal(self):
        di = Di()
        mgr = SignalManager(di)

        def handler(di, sig, frame):
            pass

        with patch.object(mgr, "_register_handler") as mock_register:
            mgr.add_handler(signal.SIGUSR1, handler)
            assert signal.SIGUSR1 in mgr.handlers
            assert handler in mgr.handlers[signal.SIGUSR1]
            mock_register.assert_called_once_with(signal.SIGUSR1)

    def test_add_handler_existing_signal_appends(self):
        di = Di()
        mgr = SignalManager(di)

        def handler1(di, sig, frame):
            pass

        def handler2(di, sig, frame):
            pass

        with patch.object(mgr, "_register_handler"):
            mgr.add_handler(signal.SIGUSR1, handler1)
            mgr.add_handler(signal.SIGUSR1, handler2)
            assert len(mgr.handlers[signal.SIGUSR1]) == 2
            assert handler1 in mgr.handlers[signal.SIGUSR1]
            assert handler2 in mgr.handlers[signal.SIGUSR1]

    def test_non_callable_raises(self):
        di = Di()
        mgr = SignalManager(di)
        with pytest.raises(TypeError):
            mgr.add_handler(signal.SIGUSR1, "not_callable")

    def test_non_int_signal_raises(self):
        di = Di()
        mgr = SignalManager(di)

        def handler(di, sig, frame):
            pass

        with pytest.raises(TypeError):
            mgr.add_handler("not_int", handler)

    def test_register_handler_calls_signal(self):
        di = Di()
        mgr = SignalManager(di)

        with patch("pokie.core.signal_manager.signal.signal") as mock_signal:
            mgr._register_handler(signal.SIGUSR1)
            mock_signal.assert_called_once()
            args = mock_signal.call_args
            assert args[0][0] == signal.SIGUSR1
