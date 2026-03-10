from unittest.mock import MagicMock

from pokie.core.middleware import ModuleRunnerMiddleware


class TestModuleRunnerMiddleware:
    def test_init_stores_app_and_pokie_app(self):
        mock_app = MagicMock()
        mock_pokie_app = MagicMock()
        middleware = ModuleRunnerMiddleware(mock_app, mock_pokie_app)
        assert middleware.app is mock_app
        assert middleware.pokie_app is mock_pokie_app

    def test_call_invokes_init_and_delegates(self):
        mock_app = MagicMock(return_value="response")
        mock_pokie_app = MagicMock()
        middleware = ModuleRunnerMiddleware(mock_app, mock_pokie_app)

        environ = {"REQUEST_METHOD": "GET"}
        start_response = MagicMock()
        result = middleware(environ, start_response)

        mock_pokie_app.init.assert_called_once()
        mock_app.assert_called_once_with(environ, start_response)
        assert result == "response"
