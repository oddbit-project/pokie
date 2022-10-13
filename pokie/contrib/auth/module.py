from pokie.contrib.auth.constants import SVC_USER, SVC_ACL, SVC_AUTH
from pokie.core import BaseModule


class Module(BaseModule):
    name = "auth"
    description = "Authentication module"

    services = {
        SVC_AUTH: 'pokie.contrib.auth.service.AuthService',
        SVC_ACL: 'pokie.contrib.auth.service.AclService',
        SVC_USER: 'pokie.contrib.auth.service.UserService',
    }

    cmd = {
        'usercreate': 'pokie.contrib.auth.cli.UserCreateCmd',
        'userinfo': 'pokie.contrib.auth.cli.UserInfoCmd',
        'usermod': 'pokie.contrib.auth.cli.UserModCmd',
    }


    def build(self):
        pass
