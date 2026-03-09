from pokie.contrib.auth.constants import SVC_USER, SVC_ACL
from pokie.core import BaseModule


class Module(BaseModule):
    name = "auth"
    description = "Authentication module"

    services = {
        SVC_ACL: "pokie.contrib.auth.service.AclService",
        SVC_USER: "pokie.contrib.auth.service.UserService",
    }

    cmd = {
        # user-related operations
        "user:create": "pokie.contrib.auth.cli.UserCreateCmd",
        "user:info": "pokie.contrib.auth.cli.UserInfoCmd",
        "user:mod": "pokie.contrib.auth.cli.UserModCmd",
        "user:list": "pokie.contrib.auth.cli.UserListCmd",
        "user:role": "pokie.contrib.auth.cli.AclUserRoleCmd",
        # acl operations
        "role:list": "pokie.contrib.auth.cli.AclRoleListCmd",
        "role:create": "pokie.contrib.auth.cli.AclRoleCreateCmd",
        "role:remove": "pokie.contrib.auth.cli.AclRoleRemoveCmd",
        "role:info": "pokie.contrib.auth.cli.AclRoleInfoCmd",
        "role:link": "pokie.contrib.auth.cli.AclRoleLinkCmd",
        "role:unlink": "pokie.contrib.auth.cli.AclRoleUnlinkCmd",
        "resource:list": "pokie.contrib.auth.cli.AclResourceListCmd",
        "resource:create": "pokie.contrib.auth.cli.AclResourceCreateCmd",
        "resource:link": "pokie.contrib.auth.cli.AclResourceLinkCmd",
        "resource:unlink": "pokie.contrib.auth.cli.AclResourceUnlinkCmd",
    }

    def build(self, parent=None):
        from pokie.contrib.auth.view import LoginView, LogoutView
        from pokie.contrib.auth.provider.session_provider import SessionProvider

        app = parent.app
        # initialize session provider
        SessionProvider(self.get_di())

        # register auth routes
        app.add_url_rule(
            "/auth/login",
            methods=["POST"],
            view_func=LoginView.as_view("auth_login"),
        )
        app.add_url_rule(
            "/auth/logout",
            methods=["GET"],
            view_func=LogoutView.as_view("auth_logout"),
        )
