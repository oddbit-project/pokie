import os.path
import sys

from rick.resource.console import AnsiColor
from rick.util.loader import load_class
from pokie.core import CliCommand
from .base import BaseCommand


class ListCmd(BaseCommand):
    description = "list available commands"

    def run(self, args) -> bool:
        color = AnsiColor()
        self.tty.write("\nusage: {} <command> [OPTIONS...]\n".format(os.path.basename(sys.argv[0])))
        self.tty.write("available commands:")
        for cmd, cmd_path in self.get_cmd_map().items():
            cls = load_class(cmd_path)

            if not cls:
                raise RuntimeError("Error: class '{}' not found while listing available CLI commands".format(cmd_path))

            if not issubclass(cls, CliCommand):
                raise RuntimeError("Error: class '{}' does not extend CliCommand".format(cmd_path))

            # show details
            self.tty.write("{} \t {}".format(color.green(cmd), color.white(cls.description)))

        return True
