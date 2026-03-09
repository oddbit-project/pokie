import io
from argparse import Namespace

from rick.resource.console import ConsoleWriter

from pokie.contrib.auth.cli.acl import (
    AclRoleCreateCmd,
    AclRoleListCmd,
    AclRoleRemoveCmd,
    AclRoleInfoCmd,
    AclResourceCreateCmd,
    AclResourceListCmd,
    AclUserRoleCmd,
)
from pokie.contrib.auth.constants import SVC_ACL, SVC_USER
from pokie.contrib.auth.dto import UserRecord
from pokie.contrib.auth.service import AclService, UserService


def make_writer():
    stdout = io.StringIO()
    stderr = io.StringIO()
    writer = ConsoleWriter(stdout=stdout, stderr=stderr)
    return writer, stdout, stderr


class TestAclRoleCreateCmd:
    def test_create_succeeds(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = AclRoleCreateCmd(pokie_di, writer=writer)
        args = Namespace(description="Test Role CLI")
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "Created role" in output

    def test_duplicate_fails(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_acl.add_role("Duplicate Role")

        writer, stdout, _ = make_writer()
        cmd = AclRoleCreateCmd(pokie_di, writer=writer)
        args = Namespace(description="Duplicate Role")
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "already exists" in output


class TestAclRoleListCmd:
    def test_lists_roles(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_acl.add_role("List Role 1")

        writer, stdout, _ = make_writer()
        cmd = AclRoleListCmd(pokie_di, writer=writer)
        result = cmd.run(None)
        assert result is True


class TestAclRoleRemoveCmd:
    def test_nonexistent_fails(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = AclRoleRemoveCmd(pokie_di, writer=writer)
        args = Namespace(id_role=99999, force=False)
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "not found" in output

    def test_existing_succeeds(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        id_role = svc_acl.add_role("Remove Role")

        writer, stdout, _ = make_writer()
        cmd = AclRoleRemoveCmd(pokie_di, writer=writer)
        args = Namespace(id_role=id_role, force=True)
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "removed" in output.lower()

    def test_in_use_without_force(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        id_role = svc_acl.add_role("In Use Role")
        user = UserRecord(username="role_use_test", password="", email="use@test.com")
        user.id = svc_user.add_user(user)
        svc_acl.add_user_role(user.id, id_role)

        writer, stdout, _ = make_writer()
        cmd = AclRoleRemoveCmd(pokie_di, writer=writer)
        args = Namespace(id_role=id_role, force=False)
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "in use" in output


class TestAclRoleInfoCmd:
    def test_existing_shows_resources(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        id_role = svc_acl.add_role("Info Role")
        svc_acl.add_resource("info_res", "Info Resource")
        svc_acl.add_role_resource(id_role, "info_res")

        writer, stdout, _ = make_writer()
        cmd = AclRoleInfoCmd(pokie_di, writer=writer)
        args = Namespace(id_role=id_role)
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "Info Resource" in output

    def test_nonexistent_fails(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = AclRoleInfoCmd(pokie_di, writer=writer)
        args = Namespace(id_role=99999)
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "not found" in output


class TestAclResourceCreateCmd:
    def test_create_succeeds(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = AclResourceCreateCmd(pokie_di, writer=writer)
        args = Namespace(id="cli_resource_1", description="CLI Resource 1")
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "Created resource" in output

    def test_duplicate_id_fails(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_acl.add_resource("dup_res", "Dup Resource")

        writer, stdout, _ = make_writer()
        cmd = AclResourceCreateCmd(pokie_di, writer=writer)
        args = Namespace(id="dup_res", description="Different Description")
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "already exists" in output

    def test_duplicate_description_fails(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_acl.add_resource("desc_res", "Existing Description")

        writer, stdout, _ = make_writer()
        cmd = AclResourceCreateCmd(pokie_di, writer=writer)
        args = Namespace(id="new_id", description="Existing Description")
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "already exists" in output


class TestAclResourceListCmd:
    def test_lists_resources(self, pokie_di, pokie_service_manager):
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        svc_acl.add_resource("list_res", "List Resource")

        writer, stdout, _ = make_writer()
        cmd = AclResourceListCmd(pokie_di, writer=writer)
        result = cmd.run(None)
        assert result is True


class TestAclUserRoleCmd:
    def test_list_user_roles(self, pokie_di, pokie_service_manager):
        svc_user = pokie_service_manager.get(SVC_USER)  # type: UserService
        svc_acl = pokie_service_manager.get(SVC_ACL)  # type: AclService
        user = UserRecord(username="roles_user", password="", email="roles@test.com")
        user.id = svc_user.add_user(user)
        id_role = svc_acl.add_role("Roles List Role")
        svc_acl.add_user_role(user.id, id_role)

        writer, stdout, _ = make_writer()
        cmd = AclUserRoleCmd(pokie_di, writer=writer)
        args = Namespace(username="roles_user")
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "Roles List Role" in output

    def test_nonexistent_user(self, pokie_di):
        writer, stdout, _ = make_writer()
        cmd = AclUserRoleCmd(pokie_di, writer=writer)
        args = Namespace(username="nonexistent_role_user")
        result = cmd.run(args)
        assert result is False
        output = stdout.getvalue()
        assert "not found" in output
