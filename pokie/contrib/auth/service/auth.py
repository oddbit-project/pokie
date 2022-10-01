from flask_login import UserMixin
from rick.base import Di
from rick.crypto.hasher import HasherInterface
from rick.crypto.hasher.bcrypt import BcryptHasher

from rick.mixin.injectable import Injectable

from pokie.contrib.auth.dto import User
from pokie.contrib.auth.service.acl import AclService
from pokie.contrib.auth.service.user import UserService
from pokie.constants import DI_SERVICE_MANAGER
from pokie.contrib.auth.constants import SVC_ACL, SVC_USER


class AuthUser(UserMixin):
    record = None  # type: User
    resources = None  # type: List
    roles = None  # type: List
    id = -1

    def __init__(self, usr: User, _di: Di):
        self.record = usr
        self.id = usr.id
        svc_acl = _di.get(DI_SERVICE_MANAGER).get(SVC_ACL)  # type: AclService
        self.resources = svc_acl.get_user_resource_list(usr.id)
        self.roles = svc_acl.get_user_role_list(usr.id)

    def can_access(self, id_resource: str) -> bool:
        return id_resource in self.resources

    def has_role(self, id_role: int):
        return id_role in self.roles


class AuthService(Injectable):

    def authenticate(self, user: User, password) -> bool:
        """
        Check if user password is valid
        :param user: User DTO
        :param password: password to check
        :return: bool
        """
        hasher = self.hasher()

        if hasher.is_valid(password, user.password):
            svc = self.user_service()
            if hasher.need_rehash(user.password):
                # update weak password hash
                svc.update_password(user.id, hasher.hash(password))
            # update lastlogin
            svc.update_lastlogin(user.id)
            return True
        return False

    def hash_pwd(self, password: str) -> str:
        return self.hasher().hash(password)

    def user_service(self) -> UserService:
        return self._di.get(DI_SERVICE_MANAGER).get(SVC_USER)

    def hasher(self) -> HasherInterface:
        return BcryptHasher()
