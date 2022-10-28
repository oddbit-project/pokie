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
        # user-related operations
        'usercreate': 'pokie.contrib.auth.cli.UserCreateCmd',
        'userinfo': 'pokie.contrib.auth.cli.UserInfoCmd',
        'usermod': 'pokie.contrib.auth.cli.UserModCmd',
        'userlist': 'pokie.contrib.auth.cli.UserListCmd',
        'acluserrole': 'pokie.contrib.auth.cli.AclUserRoleCmd',

        # acl operations
        'aclrolelist': 'pokie.contrib.auth.cli.AclRoleListCmd',
        'aclrolecreate': 'pokie.contrib.auth.cli.AclRoleCreateCmd',
        'aclroleremove': 'pokie.contrib.auth.cli.AclRoleRemoveCmd',
        'aclroleinfo': 'pokie.contrib.auth.cli.AclRoleInfoCmd',
        'aclrolelink': 'pokie.contrib.auth.cli.AclRoleLinkCmd',
        'aclroleunlink': 'pokie.contrib.auth.cli.AclRoleUnlinkCmd',

        'aclresourcelist': 'pokie.contrib.auth.cli.AclResourceListCmd',
        'aclresourcecreate': 'pokie.contrib.auth.cli.AclResourceCreateCmd',
        'aclresourcelink': 'pokie.contrib.auth.cli.AclResourceLinkCmd',
        'aclresourceunlink': 'pokie.contrib.auth.cli.AclResourceUnlinkCmd',
    }


    def build(self, parent=None):
        pass
