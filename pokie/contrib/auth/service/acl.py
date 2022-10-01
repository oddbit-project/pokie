from typing import List

from rick.mixin.injectable import Injectable

from pokie.contrib.auth.dto import AclRole
from pokie.contrib.auth.repository.acl import AclRoleRepository, AclResourceRepository
from pokie.constants import DI_DB


class AclService(Injectable):

    def get_user_roles(self, id_user: int) -> List[AclRole]:
        return self.role_repository.find_user_roles(id_user)

    def get_user_resource_list(self, id_user: int) -> List[str]:
        result = []
        for record in self.resource_repository.find_user_resources(id_user):
            result.append(record.id)
        return result

    def get_user_role_list(self, id_user: int) -> List[str]:
        result = []
        for record in self.role_repository.find_user_roles(id_user):
            result.append(record.id)
        return result

    @property
    def role_repository(self):
        return AclRoleRepository(self.get_di().get(DI_DB))

    @property
    def resource_repository(self):
        return AclResourceRepository(self.get_di().get(DI_DB))
