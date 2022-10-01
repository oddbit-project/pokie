import abc
from typing import Optional

from flask_login import UserMixin
from rick.mixin import Injectable


class AuthProvider(Injectable, abc.ABC):

    @abc.abstractmethod
    def autenticate(self, login: str, password: str) -> Optional[UserMixin]:
        pass
