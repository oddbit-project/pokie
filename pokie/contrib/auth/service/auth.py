from typing import Optional

from rick.mixin.injectable import Injectable
from rick.util.loader import load_class

from pokie.contrib.auth.service.user import AuthUser
from pokie.constants import DI_CONFIG
from pokie.interfaces.plugins.auth import AuthPlugin


class AuthService(Injectable):

    def authenticate(self, username: str, password: str) -> Optional[AuthUser]:
        for plugin in self.auth_plugins:  # type: AuthPlugin
            if plugin.valid_username(username):
                result = plugin.autenticate(username, password)
                if result is not None:
                    return result
        return None

    def update_password(self, username: str, password: str) -> bool:
        for plugin in self.auth_plugins:  # type: AuthPlugin
            if plugin.valid_username(username) and plugin.has_capability(AuthPlugin.UPDATE_PASSWORD):
                return plugin.update_password(username, password)
        return False

    @property
    def auth_plugins(self) -> list:
        di = self.get_di()
        cfg = di.get(DI_CONFIG)
        plugins = []
        auth_plugins = cfg.get('auth_plugins', [])
        if len(auth_plugins) == 0:
            raise RuntimeError("AuthService: authentication plugins missing from configuration")
        for name in auth_plugins:
            plugin = load_class(name)
            if plugin is None:
                raise RuntimeError("AuthService: auth plugin '{}' not found".format(name))
            if not issubclass(plugin, AuthPlugin):
                raise RuntimeError("AuthService: auth plugin '{}' must implement AuthPlugin interface".format(name))
            plugins.append(plugin(di))
        return plugins
