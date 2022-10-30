from pokie.contrib.base.constants import SVC_VALIDATOR
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
        'dbinit': 'pokie.contrib.base.cli.DbInitCmd',
        'dbcheck': 'pokie.contrib.base.cli.DbCheckCmd',
        'dbupdate': 'pokie.contrib.base.cli.DbUpdateCmd',

        # worker job commands
        'joblist': 'pokie.contrib.base.cli.JobListCmd',
        'jobrun': 'pokie.contrib.base.cli.JobRunCmd',
    }

    services = {
        # db-related validators
        SVC_VALIDATOR: 'pokie.contrib.base.service.ValidatorService'
    }

    jobs = [
        'pokie.contrib.base.job.IdleJob',
    ]

    def build(self, parent=None):
        init_validators(self.get_di())
