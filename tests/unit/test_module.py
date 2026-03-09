from rick.mixin import Injectable

from pokie.core.module import BaseModule


class ConcreteModule(BaseModule):
    name = "test_module"
    description = "A test module"
    services = {"svc1": "some.Service"}
    cmd = {"cmd1": "some.Command"}
    jobs = ["some.Job"]


class EmptyModule(BaseModule):
    name = "empty"
    description = ""


class TestBaseModule:
    def test_subclass_attributes(self):
        module = ConcreteModule.__new__(ConcreteModule)
        assert module.name == "test_module"
        assert module.description == "A test module"
        assert module.services == {"svc1": "some.Service"}
        assert module.cmd == {"cmd1": "some.Command"}
        assert module.jobs == ["some.Job"]

    def test_build_is_noop(self):
        module = ConcreteModule.__new__(ConcreteModule)
        result = module.build()
        assert result is None

    def test_build_with_parent(self):
        module = ConcreteModule.__new__(ConcreteModule)
        result = module.build(parent="something")
        assert result is None

    def test_empty_module_defaults(self):
        module = EmptyModule.__new__(EmptyModule)
        assert module.name == "empty"
        assert module.description == ""
        assert module.services == {}
        assert module.cmd == {}
        assert module.jobs == []

    def test_injectable_mixin(self):
        assert issubclass(BaseModule, Injectable)
