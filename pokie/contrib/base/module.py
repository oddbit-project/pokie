from pokie.contrib.base.constants import SVC_VALIDATOR, SVC_SETTINGS
from pokie.contrib.base.validators import init_validators
from pokie.core import BaseModule


class Module(BaseModule):
    name = "base"
    description = "Pokie base module"

    cmd = {
        # base commands
        'list': 'pokie.contrib.base.cli.ListCmd',
        'help': 'pokie.contrib.base.cli.HelpCmd',
        'version': 'pokie.contrib.base.cli.VersionCmd',
        'runserver': 'pokie.contrib.base.cli.RunServerCmd',

        # database-related commands
        'db:init': 'pokie.contrib.base.cli.DbInitCmd',
        'db:check': 'pokie.contrib.base.cli.DbCheckCmd',
        'db:update': 'pokie.contrib.base.cli.DbUpdateCmd',

        # worker job commands
        'job:list': 'pokie.contrib.base.cli.JobListCmd',
        'job:run': 'pokie.contrib.base.cli.JobRunCmd',

        # code generation
        'codegen:dto': 'pokie.contrib.base.cli.GenDtoCmd',
        'codegen:request': 'pokie.contrib.base.cli.GenRequestRecordCmd',
    }

    services = {
        # db-related validators
        SVC_VALIDATOR: 'pokie.contrib.base.service.ValidatorService',
        # settings service
        SVC_SETTINGS: 'pokie.contrib.base.service.SettingsService'
    }

    jobs = [
        'pokie.contrib.base.job.IdleJob',
    ]

    def build(self, parent=None):
        init_validators(self.get_di())
