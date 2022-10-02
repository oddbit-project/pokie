from pokie.contrib.auth.constants import SVC_USER, SVC_ACL, SVC_AUTH
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
    }

    def build(self):
        pass
