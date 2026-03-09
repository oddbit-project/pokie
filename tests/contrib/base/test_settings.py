from pokie.contrib.base.constants import SVC_SETTINGS
from pokie.contrib.base.service import SettingsService


class TestSettings:
    def test_settings(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_SETTINGS)  # type: SettingsService

        assert len(svc.list()) == 0
        for i in range(1, 10):
            svc.upsert("module1", "setting_{}".format(i), str(i))
        assert len(svc.list()) == 9

        record = svc.by_key("module1", "setting_5")
        assert record is not None
        assert record.value == "5"

        svc.upsert(record.module, record.key, "foo")
        record = svc.by_key("module1", "setting_5")
        assert record is not None
        assert record.value == "foo"

    def test_by_module(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_SETTINGS)  # type: SettingsService
        svc.upsert("mod_a", "key1", "val1")
        svc.upsert("mod_a", "key2", "val2")
        svc.upsert("mod_b", "key3", "val3")

        result = svc.by_module("mod_a")
        assert len(result) == 2
        for r in result:
            assert r.module == "mod_a"

    def test_by_key_nonexistent(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_SETTINGS)  # type: SettingsService
        result = svc.by_key("nonexistent_module", "nonexistent_key")
        assert result is None

    def test_delete(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_SETTINGS)  # type: SettingsService
        svc.upsert("mod_del", "key_del", "val_del")
        record = svc.by_key("mod_del", "key_del")
        assert record is not None

        svc.delete("mod_del", "key_del")
        record = svc.by_key("mod_del", "key_del")
        assert record is None

    def test_delete_nonexistent(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_SETTINGS)  # type: SettingsService
        svc.delete("nonexistent", "nonexistent")  # should not raise
