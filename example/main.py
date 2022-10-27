from rick.resource.config import EnvironmentConfig

from pokie.config.template import BaseConfigTemplate, PgConfigTemplate
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory


# base configuration
class Config(EnvironmentConfig, BaseConfigTemplate, PgConfigTemplate):
    pass


# load configuration from ENV
cfg = Config().build()

# modules to load & initialize
modules = ['pokie.contrib.auth', 'module']

# factories to run
factories = [PgSqlFactory, ]

# build app
main = FlaskApplication(cfg)
app = main.build(modules, factories)

if __name__ == '__main__':
    main.cli()
