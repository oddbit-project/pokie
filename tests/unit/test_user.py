from pokie.contrib.auth.user import User, UserInterface


class TestUser:
    def test_anonymous_user(self):
        user = User()
        assert user.is_anonymous is True
        assert user.is_authenticated is False
        assert user.is_active is False
        assert user.get_id() is None
        assert user.get_record() is None
        assert user.get_roles() == []
        assert user.get_resources() == []

    def test_authenticated_user(self):
        user = User(id_user=42)
        assert user.is_anonymous is False
        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.get_id() == "42"

    def test_is_active_with_record_active_true(self):
        class FakeRecord:
            active = True

        user = User(id_user=1, record=FakeRecord())
        assert user.is_active is True

    def test_is_active_with_record_active_false(self):
        class FakeRecord:
            active = False

        user = User(id_user=1, record=FakeRecord())
        assert user.is_active is False

    def test_is_active_with_record_no_active_attr(self):
        class FakeRecord:
            pass

        user = User(id_user=1, record=FakeRecord())
        assert user.is_active is False

    def test_can_access(self):
        user = User(id_user=1, resources=["res1", "res2", "res3"])
        assert user.can_access("res1") is True
        assert user.can_access("res2") is True
        assert user.can_access("res4") is False

    def test_has_role(self):
        user = User(id_user=1, roles=[1, 2, 3])
        assert user.has_role(1) is True
        assert user.has_role(3) is True
        assert user.has_role(5) is False

    def test_get_roles(self):
        roles = [1, 2, 3]
        user = User(id_user=1, roles=roles)
        assert user.get_roles() == roles

    def test_get_resources(self):
        resources = ["a", "b", "c"]
        user = User(id_user=1, resources=resources)
        assert user.get_resources() == resources

    def test_kwargs_set_as_attributes(self):
        user = User(id_user=1, custom_field="hello", another=42)
        assert user.custom_field == "hello"
        assert user.another == 42

    def test_user_interface_compliance(self):
        assert issubclass(User, UserInterface)

    def test_get_record(self):
        record = {"name": "test"}
        user = User(id_user=1, record=record)
        assert user.get_record() == record

    def test_default_roles_resources(self):
        user = User(id_user=1)
        assert user.roles == []
        assert user.resources == []
