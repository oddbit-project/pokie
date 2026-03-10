import pytest
from rick.crypto.hasher.bcrypt import BcryptHasher

from pokie.contrib.auth.constants import SVC_USER, SVC_ACL
from pokie.contrib.auth.dto import UserRecord
from pokie.contrib.auth.provider.session_provider import SessionProvider, build_user_acl
from pokie.contrib.auth.service import UserService, AclService
from pokie.contrib.auth.user import User


class TestSessionProvider:
    def _create_test_user(self, pokie_service_manager, username="session_user", password="test123"):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        pwd_hash = BcryptHasher().hash(password)
        record = UserRecord(
            username=username,
            email="{}@test.com".format(username),
            password=pwd_hash,
            active=True,
        )
        record.id = svc_user.add_user(record)
        return record

    def test_build_user_acl(self, pokie_di, pokie_service_manager):
        user_record = self._create_test_user(pokie_service_manager)

        # create a role and assign it
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        id_role = svc_acl.add_role("test_role")
        svc_acl.add_resource("test_res", "test resource")
        svc_acl.add_role_resource(id_role, "test_res")
        svc_acl.add_user_role(user_record.id, id_role)

        user = build_user_acl(pokie_di, user_record)
        assert isinstance(user, User)
        assert user.is_authenticated is True
        assert id_role in user.get_roles()
        assert "test_res" in user.get_resources()

    def test_login_invalid_credentials(self, pokie_di, pokie_service_manager, pokie_app):
        self._create_test_user(pokie_service_manager)
        with pokie_app.test_request_context():
            provider = SessionProvider(pokie_di)
            result = provider.login("session_user", "wrong_password")
            assert result is None

    def test_get_user_raises(self, pokie_di, pokie_app):
        with pokie_app.test_request_context():
            provider = SessionProvider(pokie_di)
            with pytest.raises(RuntimeError, match="not available directly"):
                provider.get_user(None)

    def test_logout_no_error(self, pokie_di, pokie_app):
        with pokie_app.test_request_context():
            provider = SessionProvider(pokie_di)
            provider.logout()  # should not raise

    def test_build_user_acl_no_roles(self, pokie_di, pokie_service_manager):
        user_record = self._create_test_user(pokie_service_manager, username="norole_user")
        user = build_user_acl(pokie_di, user_record)
        assert isinstance(user, User)
        assert user.get_roles() == []
        assert user.get_resources() == []
