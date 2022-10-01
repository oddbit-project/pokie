from typing import Optional

from flask_login import UserMixin

from .provider import AuthProvider


class DbAuthProvider(AuthProvider):

    def autenticate(self, login: str, password: str) -> Optional[UserMixin]:
        return None

    @property
    def repository_user(self):
        pass
