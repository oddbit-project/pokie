import tty
from typing import List

from rick.resource.console import AnsiColor
from rick.util.loader import load_class
from pokie.constants import DI_APP
from pokie.core import CliCommand


class BaseCommand(CliCommand):

    def get_modules(self) -> dict:
        return self.get_di().get(DI_APP).modules

    def get_cmd_map(self) -> dict:
        result = {}
        for _, module in self.get_modules().items():
            for cmd, cmd_class in module.cmd.items():
                result[cmd] = cmd_class
        return result

    def run(self, args) -> bool:
        di = self.get_di()
        color = AnsiColor()
        self.tty.write("Available commands:\n")
        for _, module in di.get(DI_APP).modules.items():
            for cmd, cmd_path in module.cmd.items():
                cls = load_class(cmd_path)
                if not cls:
                    raise RuntimeError("Error: class '{}' not found while listing available CLI commands".format(cmd_path))
                if not issubclass(cls, CliCommand):
                    raise RuntimeError("Error: class '{}' does not extend CliCommand".format(cmd_path))
                obj = cls(di)
                self.tty.write("{} \t {}".format(color.green(cmd), color.white(obj.description)))

        return True
