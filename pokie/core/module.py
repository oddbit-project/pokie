import abc

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

    @abc.abstractmethod
    def build(self, parent=None):
        """
        Initialize module internals
        :param parent: FlaskApplication instance
        :return:
        """
        pass
