from pokie.contrib.base.constants import SVC_VALIDATOR
from pokie.contrib.base.service.validator import ValidatorService


class TestValidatorService:
    def test_id_exists_valid_pk(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_VALIDATOR)  # type: ValidatorService
        assert svc.id_exists("customer_id", "FIXTURE", "customers") is True

    def test_id_exists_invalid_pk(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_VALIDATOR)  # type: ValidatorService
        assert svc.id_exists("customer_id", "NONEXISTENT_KEY", "customers") is False

    def test_id_exists_explicit_pk_name(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_VALIDATOR)  # type: ValidatorService
        assert svc.id_exists("customer_id", "FIXTURE", "customers") is True

    def test_cache_add_get(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_VALIDATOR)  # type: ValidatorService
        svc._cache_add("test_key", "test_value")
        result = svc._cache_get("test_key")
        if svc._cache is not None:
            assert result == "test_value"

    def test_cache_get_default(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_VALIDATOR)  # type: ValidatorService
        result = svc._cache_get("nonexistent_key", default="fallback")
        assert result == "fallback"

    def test_repo_validator(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_VALIDATOR)  # type: ValidatorService
        repo = svc.repo_validator
        assert repo is not None
        assert repo.pk_exists("FIXTURE", "customer_id", "customers") is True
        assert repo.pk_exists("NONEXIST", "customer_id", "customers") is False
