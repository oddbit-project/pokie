from rick.resource.config import EnvironmentConfig
from pokie.config.template import (
    BaseConfigTemplate,
    PgConfigTemplate,
    TestConfigTemplate,
)
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory
from pokie.contrib.base.module import Module


class Config(
    EnvironmentConfig, BaseConfigTemplate, PgConfigTemplate, TestConfigTemplate
):
    # ENV var with optional plugins
    POKIE_PLUGINS = []

    TEST_MANAGE_DB = True
    TEST_DB_SSL = False


def main(args=None):
    # patch base module to only allow some commands
    allowed_cmds = [
        "list",
        "help",
        "version",
        "db:init",
        "db:check",
        "codegen:dto",
        "codegen:request",
        "codegen:module",
        "codegen:app",
    ]
    cli_list = {}
    for cmd, cls in getattr(Module, "cmd", {}).items():
        if cmd in allowed_cmds:
            cli_list[cmd] = cls
    setattr(Module, "cmd", cli_list)

    # build cli app
    cfg = Config().build()
    pokie_app = FlaskApplication(cfg)
    pokie_app.build(
        cfg.get("pokie_plugins"),
        [
            PgSqlFactory,
        ],
    )
    pokie_app.cli()
