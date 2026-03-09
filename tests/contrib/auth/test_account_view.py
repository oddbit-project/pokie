from rick.crypto.hasher.bcrypt import BcryptHasher

from pokie.constants import HTTP_OK, HTTP_BADREQ, HTTP_NOAUTH
from pokie.contrib.auth.constants import SVC_USER
from pokie.contrib.auth.dto import UserRecord
from pokie.contrib.auth.service import UserService
from pokie.test import PokieClient


class TestAccountView:
    def _create_test_user(self, pokie_service_manager, username="testlogin", password="testpass123"):
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

    def test_login_missing_fields(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.post("/auth/login", data={})
            assert result.code == HTTP_BADREQ
            assert result.success is False

    def test_login_invalid_credentials(self, pokie_app, pokie_service_manager):
        self._create_test_user(pokie_service_manager)
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.post(
                "/auth/login",
                data={"username": "testlogin", "password": "wrongpassword"},
            )
            assert result.code == HTTP_BADREQ
            assert result.success is False
            assert "invalid credentials" in result.error_message

    def test_login_nonexistent_user(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.post(
                "/auth/login",
                data={"username": "no_such_user", "password": "pass"},
            )
            assert result.code == HTTP_BADREQ
            assert result.success is False

    def test_logout_unauthenticated(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            result = client.get("/auth/logout")
            assert result.code == HTTP_NOAUTH
