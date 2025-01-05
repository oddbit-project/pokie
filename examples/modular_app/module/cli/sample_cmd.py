from argparse import ArgumentParser

from pokie.core import CliCommand


class SampleCmd(CliCommand):
    description = "sample command"

    def arguments(self, parser: ArgumentParser):
        parser.add_argument("--verbosity", help="increase output verbosity")

    def run(self, args) -> bool:
        self.tty.write("sample command executed successfully")
        return True
