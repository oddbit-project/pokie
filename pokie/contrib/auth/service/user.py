from typing import Optional

from rick.mixin import Injectable

from pokie.contrib.auth.repository.user import UserRepository
from pokie.constants import DI_SERVICE_MANAGER, DI_DB
from rick.util.datetime import iso8601_now
from pokie.contrib.auth.dto import User


class UserService(Injectable):

    def get_by_username(self, username: str) -> Optional[User]:
        return self.user_repository.find_by_username(username)

    def update_lastlogin(self, id_user: int):
        self.user_repository.update(User(id=id_user, last_login=iso8601_now()))

    def update_password(self, id_user: int, password_hash: str):
        self.user_repository.update(User(id=id_user, password=password_hash))

    @property
    def user_repository(self) -> UserRepository:
        return UserRepository(self._di.get(DI_SERVICE_MANAGER).get(DI_DB))
