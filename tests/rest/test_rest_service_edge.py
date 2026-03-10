import pytest

from pokie.rest import RestService
from pokie.rest.service_mixin import RestServiceMixin
from pokie_test.dto import CustomerRecord
from pokie_test.repository import CustomerRepository


class TestRestServiceEdge:
    def test_missing_record_class(self, pokie_di):
        svc = RestService(pokie_di)
        with pytest.raises(RuntimeError, match="Missing record class"):
            _ = svc.repository

    def test_set_record_class(self, pokie_di):
        svc = RestService(pokie_di)
        svc.set_record_class(CustomerRecord)
        assert svc._record_cls == CustomerRecord

    def test_set_repository_class(self, pokie_di):
        svc = RestService(pokie_di)
        svc.set_repository_class(CustomerRepository)
        assert svc._repository_cls == CustomerRepository

    def test_default_repository_creation(self, pokie_di):
        svc = RestService(pokie_di)
        svc.set_record_class(CustomerRecord)
        repo = svc.repository
        assert repo is not None

    def test_custom_repository_creation(self, pokie_di):
        svc = RestService(pokie_di)
        svc.set_record_class(CustomerRecord)
        svc.set_repository_class(CustomerRepository)
        repo = svc.repository
        assert isinstance(repo, CustomerRepository)


class TestRestServiceMixin:
    def test_repository_raises(self):
        mixin = RestServiceMixin()
        with pytest.raises(RuntimeError, match="must be overridden"):
            _ = mixin.repository
