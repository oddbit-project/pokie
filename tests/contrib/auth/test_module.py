from pokie.contrib.auth.constants import SVC_ACL, SVC_USER
from pokie.contrib.auth.module import Module
from pokie.test import PokieClient


class TestAuthModule:
    def test_module_name(self):
        assert Module.name == "auth"

    def test_module_description(self):
        assert Module.description == "Authentication module"

    def test_module_services(self):
        assert SVC_ACL in Module.services
        assert SVC_USER in Module.services

    def test_module_cmd_registered(self):
        assert "user:create" in Module.cmd
        assert "user:info" in Module.cmd
        assert "user:mod" in Module.cmd
        assert "user:list" in Module.cmd
        assert "role:list" in Module.cmd
        assert "role:create" in Module.cmd
        assert "role:remove" in Module.cmd
        assert "role:info" in Module.cmd
        assert "resource:list" in Module.cmd
        assert "resource:create" in Module.cmd

    def test_build_registers_routes(self, pokie_app):
        with pokie_app.test_client() as client:
            client = PokieClient(client)
            # verify auth routes exist by checking they return something other than generic 404
            result = client.post("/auth/login", data={})
            # login with empty data returns 400, proving the route exists
            assert result.code == 400
