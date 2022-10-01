from typing import List

from rick_db import Repository
from rick_db.sql import Select

from pokie.contrib.auth.dto import AclRole, AclUserRole, AclResource, AclRoleResource


class AclRoleRepository(Repository):

    def __init__(self, db):
        super().__init__(db, AclRole)

    def find_user_roles(self, id_user: int) -> List[AclRole]:
        key = '__acl__:find_user_roles'
        sql = self._cache_get(key)
        if not sql:
            sql, _ = Select() \
                .join(AclUserRole, AclUserRole.id_role, '=', AclRole.id) \
                .where(AclUserRole.id_user, '=', id_user) \
                .order(AclRole.id) \
                .assemble()
            self._cache_set(key, sql)
        with self._db.cursor() as c:
            return c.fetchall(sql, [id_user], cls=AclRole)


class AclResourceRepository(Repository):

    def __init__(self, db):
        super().__init__(db, AclResource)

    def find_user_resources(self, id_user: int) -> List[AclResource]:
        key = '__acl__:find_user_resources'
        sql = self._cache_get(key)
        if not sql:
            sql, _ = Select() \
                .join(AclRoleResource, AclRoleResource.id_resource, '=', AclResource.id) \
                .join(AclUserRole, AclUserRole.id_role, '=', AclRoleResource.id_role) \
                .where(AclUserRole.id_user, '=', id_user) \
                .assemble()
            self._cache_set(key, sql)

        with self._db.cursor() as c:
            return c.fetchall(sql, [id_user], cls=AclRole)
