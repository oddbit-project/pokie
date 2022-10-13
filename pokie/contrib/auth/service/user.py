from typing import Optional

from rick.mixin import Injectable

from pokie.contrib.auth.repository.user import UserRepository
from pokie.constants import DI_SERVICE_MANAGER, DI_DB
from rick.util.datetime import iso8601_now
from pokie.contrib.auth.dto import UserRecord


class UserService(Injectable):

    def get_by_username(self, username: str) -> Optional[UserRecord]:
        return self.user_repository.find_by_username(username)

    def update_lastlogin(self, id_user: int):
        self.user_repository.update(UserRecord(id=id_user, last_login=iso8601_now()))

    def update_password(self, id_user: int, password_hash: str):
        self.user_repository.update(UserRecord(id=id_user, password=password_hash))

    def add_user(self, record:UserRecord) -> int:
        """
        Creates a new user
        :param record:
        :return:
        """
        return self.user_repository.insert_pk(record)

    def update_user(self, record:UserRecord):
        return self.user_repository.update(record)

    @property
    def user_repository(self) -> UserRepository:
        return UserRepository(self._di.get(DI_DB))
