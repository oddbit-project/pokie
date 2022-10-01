from typing import Union

from rick_db import Repository

from pokie.contrib.auth.dto import User


class UserRepository(Repository):

    def __init__(self, db):
        super().__init__(db, User)

    def find_by_username(self, username: str) -> Union[User, None]:
        key = '__user__:find_by_username'
        sql = self._cache_get(key)
        if not sql:
            sql = self.select() \
                .where(User.username, '=', username) \
                .assemble()
            self._cache_set(key, sql)
        with self._db.cursor() as c:
            return c.fetchone(sql, [username, 1], cls=User)
