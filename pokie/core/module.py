import abc

from rick.base import Di
from rick.mixin import Injectable


class BaseModule(Injectable, abc.ABC):
    # base module name; must be unique
    name = ""

    # module extended description
    description = ""

    # service mapper
    services = {}

    # cli command mapper
    cmd = {}

    # events
    events = {}

    # jobs
    jobs = []

    # fixtures
    fixtures = []

    def __init__(self, di: Di):
        super().__init__(di)
        # ensure each instance has its own copy of mutable defaults
        # if not explicitly overridden at the class level
        if "services" not in type(self).__dict__:
            self.services = {}
        if "cmd" not in type(self).__dict__:
            self.cmd = {}
        if "events" not in type(self).__dict__:
            self.events = {}
        if "jobs" not in type(self).__dict__:
            self.jobs = []
        if "fixtures" not in type(self).__dict__:
            self.fixtures = []

    def build(self, parent=None):
        """
        Initialize module internals
        :param parent: FlaskApplication instance
        :return:
        """
        pass
