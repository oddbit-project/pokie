from pokie.contrib.auth.constants import SVC_USER, SVC_ACL, SVC_AUTH
from pokie.core import BaseModule


class Module(BaseModule):
    name = "base"
    description = "Pokie base module"

    cmd = {
        'list': 'pokie.contrib.base.cli.ListCmd',
        'help': 'pokie.contrib.base.cli.HelpCmd',
    }

    def build(self):
        pass
