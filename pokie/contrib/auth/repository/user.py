from typing import Union

from rick_db import Repository

from pokie.contrib.auth.dto import UserRecord


class UserRepository(Repository):

    def __init__(self, db):
        super().__init__(db, UserRecord)

    def find_by_username(self, username: str) -> Union[UserRecord, None]:
        key = '__user__:find_by_username'
        sql = self._cache_get(key)
        if not sql:
            sql, _ = self.select() \
                .where(UserRecord.username, '=', username) \
                .assemble()
            self._cache_set(key, sql)
        with self._db.cursor() as c:
            return c.fetchone(sql, [username], cls=UserRecord)
