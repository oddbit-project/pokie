import pytest

from pokie.contrib.base.constants import SVC_FIXTURE
from pokie.contrib.base.dto import FixtureRecord
from pokie.contrib.base.repository.fixture import FixtureRepository
from pokie.contrib.base.service.fixture import FixtureService, FixtureError
from pokie_test.repository import CustomerRepository


class TestFixtures:
    def test_load_fixtures(self, pokie_db):
        # check if table/record exists
        repo = FixtureRepository(pokie_db)
        f_list = repo.fetch_where(
            [
                (FixtureRecord.name, "=", "pokie_test.fixtures.ExampleFixture"),
            ]
        )
        assert f_list is not None
        assert len(f_list) == 1

        # fixture should have been loaded
        repo = CustomerRepository(pokie_db)
        assert repo.fetch_pk("FIXTURE") is not None

    def test_scan(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_FIXTURE)  # type: FixtureService
        result = svc.scan()
        assert isinstance(result, list)

    def test_execute_nonexistent_class(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_FIXTURE)  # type: FixtureService
        with pytest.raises(FixtureError, match="cannot locate"):
            svc.execute("nonexistent.module.Class")

    def test_execute_invalid_class(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_FIXTURE)  # type: FixtureService
        with pytest.raises(FixtureError, match="must implement"):
            svc.execute("pokie.contrib.base.dto.FixtureRecord")

    def test_list(self, pokie_service_manager):
        svc = pokie_service_manager.get(SVC_FIXTURE)  # type: FixtureService
        result = svc.list()
        assert isinstance(result, list)
