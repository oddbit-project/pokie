import io
from argparse import Namespace

from rick.crypto.hasher.bcrypt import BcryptHasher
from rick.resource.console import ConsoleWriter

from pokie.contrib.auth.cli.user import UserCreateCmd, UserInfoCmd, UserListCmd, UserModCmd
from pokie.contrib.auth.constants import SVC_USER
from pokie.contrib.auth.dto import UserRecord
from pokie.contrib.auth.service import UserService
from pokie.contrib.base.validators.pk import init_validators


def make_writer():
    stdout = io.StringIO()
    stderr = io.StringIO()
    writer = ConsoleWriter(stdout=stdout, stderr=stderr)
    return writer, stdout, stderr


class TestUserCreateCmd:
    def test_valid_creation(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = UserCreateCmd(pokie_di, writer=writer)
        args = Namespace(
            username="cli_user1",
            email="cli_user1@test.com",
            first_name="John",
            last_name="Doe",
            password=False,
            enabled=True,
            admin=False,
        )
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "Created user" in output

    def test_invalid_email(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = UserCreateCmd(pokie_di, writer=writer)
        args = Namespace(
            username="cli_user2",
            email="invalid",
            first_name=None,
            last_name=None,
            password=False,
            enabled=True,
            admin=False,
        )
        result = cmd.run(args)
        assert result is False

    def test_duplicate_username(self, pokie_di, pokie_service_manager):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        record = UserRecord(username="dup_user", password="", email="dup@test.com")
        svc_user.add_user(record)

        writer, stdout, _ = make_writer()
        cmd = UserCreateCmd(pokie_di, writer=writer)
        args = Namespace(
            username="dup_user",
            email="dup2@test.com",
            first_name=None,
            last_name=None,
            password=False,
            enabled=True,
            admin=False,
        )
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "already exists" in output


class TestUserInfoCmd:
    def _create_user(self, pokie_service_manager, username="info_user"):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        record = UserRecord(
            username=username,
            password="",
            email="{}@test.com".format(username),
            first_name="Test",
            last_name="User",
        )
        record.id = svc_user.add_user(record)
        return record

    def test_existing_user(self, pokie_di, pokie_service_manager):
        init_validators(pokie_di)
        self._create_user(pokie_service_manager)
        writer, stdout, _ = make_writer()
        cmd = UserInfoCmd(pokie_di, writer=writer)
        args = Namespace(username="info_user")
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "info_user" in output

    def test_nonexistent_user(self, pokie_di):
        init_validators(pokie_di)
        writer, stdout, _ = make_writer()
        cmd = UserInfoCmd(pokie_di, writer=writer)
        args = Namespace(username="nonexistent_user_xyz")
        result = cmd.run(args)
        assert result is False


class TestUserListCmd:
    def test_list_output(self, pokie_di, pokie_service_manager):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        svc_user.add_user(UserRecord(username="list_user1", password="", email="l1@test.com"))
        svc_user.add_user(UserRecord(username="list_user2", password="", email="l2@test.com"))

        writer, stdout, _ = make_writer()
        cmd = UserListCmd(pokie_di, writer=writer)
        args = Namespace(offset=0, count=0, id=False)
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "Displaying" in output

    def test_negative_offset(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = UserListCmd(pokie_di, writer=writer)
        args = Namespace(offset=-1, count=0, id=False)
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "offset cannot be negative" in output

    def test_negative_count(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = UserListCmd(pokie_di, writer=writer)
        args = Namespace(offset=0, count=-1, id=False)
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "count cannot be negative" in output

    def test_sort_by_id(self, pokie_di, pokie_service_manager):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        svc_user.add_user(UserRecord(username="sort_user", password="", email="s@test.com"))

        writer, stdout, _ = make_writer()
        cmd = UserListCmd(pokie_di, writer=writer)
        args = Namespace(offset=0, count=0, id=True)
        result = cmd.run(args)
        assert result is True


class TestUserModCmd:
    def _create_user(self, pokie_di, pokie_service_manager, username="mod_user"):
        init_validators(pokie_di)
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        pwd_hash = BcryptHasher().hash("modpass123")
        record = UserRecord(
            username=username,
            password=pwd_hash,
            email="{}@test.com".format(username),
            active=True,
            admin=False,
        )
        record.id = svc_user.add_user(record)
        return record

    def test_no_options(self, pokie_di, pokie_service_manager):
        self._create_user(pokie_di, pokie_service_manager)
        writer, stdout, _ = make_writer()
        cmd = UserModCmd(pokie_di, writer=writer)
        args = Namespace(
            username="mod_user",
            password=False,
            noadmin=False,
            admin=False,
            enabled=False,
            disabled=False,
        )
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "missing modification options" in output

    def test_mutually_exclusive_admin(self, pokie_di, pokie_service_manager):
        self._create_user(pokie_di, pokie_service_manager)
        writer, stdout, _ = make_writer()
        cmd = UserModCmd(pokie_di, writer=writer)
        args = Namespace(
            username="mod_user",
            password=False,
            noadmin=True,
            admin=True,
            enabled=False,
            disabled=False,
        )
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "mutually exclusive" in output

    def test_mutually_exclusive_status(self, pokie_di, pokie_service_manager):
        self._create_user(pokie_di, pokie_service_manager)
        writer, stdout, _ = make_writer()
        cmd = UserModCmd(pokie_di, writer=writer)
        args = Namespace(
            username="mod_user",
            password=False,
            noadmin=False,
            admin=False,
            enabled=True,
            disabled=True,
        )
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "mutually exclusive" in output

    def test_set_admin(self, pokie_di, pokie_service_manager):
        self._create_user(pokie_di, pokie_service_manager)
        writer, stdout, _ = make_writer()
        cmd = UserModCmd(pokie_di, writer=writer)
        args = Namespace(
            username="mod_user",
            password=False,
            noadmin=False,
            admin=True,
            enabled=False,
            disabled=False,
        )
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "admin privileges" in output

    def test_disable_user(self, pokie_di, pokie_service_manager):
        self._create_user(pokie_di, pokie_service_manager)
        writer, stdout, _ = make_writer()
        cmd = UserModCmd(pokie_di, writer=writer)
        args = Namespace(
            username="mod_user",
            password=False,
            noadmin=False,
            admin=False,
            enabled=False,
            disabled=True,
        )
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "disabled" in output

    def test_nonexistent_user(self, pokie_di):
        init_validators(pokie_di)
        writer, stdout, _ = make_writer()
        cmd = UserModCmd(pokie_di, writer=writer)
        args = Namespace(
            username="nonexistent_mod_user",
            password=False,
            noadmin=False,
            admin=True,
            enabled=False,
            disabled=False,
        )
        result = cmd.run(args)
        assert result is False
