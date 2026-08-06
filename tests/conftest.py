import os

import pytest

pytest_plugins = [
    "tests.unit.fixtures",
]

# Test services.
#
# `python main.py pytest` used to need a hand-provisioned PostgreSQL plus matching
# credentials in env.sh. That is a setup step per developer machine, and when it
# drifts the whole suite fails rather than the database-backed part of it: the
# plugin's `pokie_app` fixture is autouse, so a bad password errors even tests that
# never touch a database. Containers remove the step — a clean checkout with Docker
# running is enough.
#
# CI (.github/workflows/ci.yml) and tox (tox.ini) already start their own services,
# so they set POKIE_TEST_CONTAINERS=0 and keep using them; the credentials below
# deliberately match theirs so a test cannot depend on which mechanism provisioned it.

POSTGRES_IMAGE = "postgres:14-alpine"
REDIS_IMAGE = "redis:7-alpine"

DB_NAME = "test_pokie"
DB_USER = "pokieUser"
DB_PASSWORD = "somePassword"

_DISABLED = ("0", "false", "no", "off")


def _containers_enabled() -> bool:
    """Should this session provision its own services?

    Explicitly disabled wins. Otherwise containers are used when testcontainers is
    importable, and when it is not we stay out of the way and leave whatever
    TEST_DB_* / REDIS_* the environment already carries — which is what an
    installation without the dev extras, or a developer pointing at their own
    database, has.
    """
    if os.getenv("POKIE_TEST_CONTAINERS", "").strip().lower() in _DISABLED:
        return False
    try:
        import testcontainers  # noqa: F401
    except ImportError:
        return False
    return True


def _load_containers():
    try:  # testcontainers >= 4.15
        from testcontainers.community.postgres import PostgresContainer
        from testcontainers.community.redis import RedisContainer
    except ImportError:  # older layout, deprecated in 4.15
        from testcontainers.postgres import PostgresContainer
        from testcontainers.redis import RedisContainer
    return PostgresContainer, RedisContainer


@pytest.fixture(scope="session", autouse=True)
def pokie_test_services():
    """Provision PostgreSQL and Redis for the session, and publish their addresses.

    Session-scoped AND autouse so it is set up before `pokie_app`, the
    function-scoped autouse fixture in `pokie.test.plugin` that builds the
    application under test. With TEST_SHARE_CTX false (the default) `pokie_app`
    re-runs `build_pokie()`, so the environment set here is the configuration the
    application reads — which is why this sets environment variables rather than
    poking at an already-built config container.
    """
    if not _containers_enabled():
        yield
        return

    postgres_cls, redis_cls = _load_containers()

    postgres = postgres_cls(
        POSTGRES_IMAGE, username=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
    )
    redis = redis_cls(REDIS_IMAGE)

    with postgres, redis:
        db_host = postgres.get_container_host_ip()
        db_port = str(postgres.get_exposed_port(5432))

        # what the test plugin uses to create/drop the per-run database
        os.environ["TEST_DB_HOST"] = db_host
        os.environ["TEST_DB_PORT"] = db_port
        os.environ["TEST_DB_NAME"] = DB_NAME
        os.environ["TEST_DB_USER"] = DB_USER
        os.environ["TEST_DB_PASSWORD"] = DB_PASSWORD
        os.environ["TEST_DB_SSL"] = "0"

        # PgSqlFactory reads DB_*; kept in step so a test that resolves DI_DB before
        # the plugin replaces it does not reach for a database that is not there
        os.environ["DB_HOST"] = db_host
        os.environ["DB_PORT"] = db_port
        os.environ["DB_NAME"] = DB_NAME
        os.environ["DB_USER"] = DB_USER
        os.environ["DB_PASSWORD"] = DB_PASSWORD
        os.environ["DB_SSL"] = "0"

        os.environ["REDIS_HOST"] = redis.get_container_host_ip()
        os.environ["REDIS_PORT"] = str(redis.get_exposed_port(6379))
        os.environ["REDIS_PASSWORD"] = ""
        os.environ["REDIS_SSL"] = "0"

        yield
