import os.path
import sys
from argparse import ArgumentParser

from rick.resource.console import AnsiColor
from rick.util.loader import load_class
from pokie.core import CliCommand
from pokie.util.cli_args import ArgParser
from .base import BaseCommand


class HelpCmd(BaseCommand):
    description = "display usage information for a given command"

    def arguments(self, parser: ArgumentParser):
        parser.add_argument('command', type=str, help="command to get usage details")

    def run(self, args) -> bool:
        map = self.get_cmd_map()
        if args.command not in map.keys():
            self.tty.error("Error: command '{}' not found".format(args.command))
            return False

        cls = load_class(map[args.command])
        handler = cls(self.get_di())  # type: CliCommand
        self.show(args.command, handler)
        return True

    def show(self, cmd, cmd_object):
        """
        Show command detail
        :param cmd: command
        :param cmd_object: command object
        :return:
        """
        program = os.path.basename(sys.argv[0])

        self.tty.write("{}: {}\n".format(cmd, cmd_object.description))
        self.tty.write("usage: {} {} [OPTIONS...]\n".format(program, cmd))

        parser = ArgParser(add_help=False)
        cmd_object.arguments(parser)
        self.tty.write(parser.format_parameters())
