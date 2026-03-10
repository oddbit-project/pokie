from flask_login import login_user, logout_user
from rick.event import EventManager

from pokie.constants import DI_EVENTS, DI_SERVICES
from pokie.contrib.auth.constants import SVC_USER, SVC_ACL
from pokie.contrib.auth.service import UserService, AclService
from pokie.contrib.auth.provider.session_provider import build_user_acl
from pokie.http.view import PokieView, PokieAuthView
from rick.form import field, RequestRecord


class LoginRequest(RequestRecord):
    fields = {
        "username": field(validators="required"),
        "password": field(validators="required"),
        "remember": field(validators="bool"),
    }


class LoginView(PokieView):
    request_class = LoginRequest

    def post(self):
        username = self.request.get("username")
        pwd = self.request.get("password")
        remember = bool(self.request.get("remember"))

        user_record = self.svc_user().authenticate(username, pwd)
        if user_record is None:
            return self.error("invalid credentials")

        user = build_user_acl(self.di, user_record)

        self.mgr_event().dispatch(self.di, "afterLogin", user=user)

        # flask-login
        login_user(user, remember)

        return self.success(user_record.asdict())

    def mgr_event(self) -> EventManager:
        return self.di.get(DI_EVENTS)

    def svc_user(self) -> UserService:
        return self.get_service(SVC_USER)

    def svc_acl(self) -> AclService:
        return self.get_service(SVC_ACL)


class LogoutView(PokieAuthView):
    def get(self):
        logout_user()
        return self.success()
