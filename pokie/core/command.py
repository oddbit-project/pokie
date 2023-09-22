from abc import ABC
from argparse import ArgumentParser

from rick.base import Di
from rick.resource.console import ConsoleWriter
from rick.mixin import Injectable

from pokie.constants import DI_TTY


class CliCommand(ABC, Injectable):
    description = "command description"
    skipargs = False

    def __init__(self, di: Di, writer=None):
        self.set_di(di)
        if not writer:
            writer = di.get(DI_TTY) if di.has(DI_TTY) else ConsoleWriter()
        self.tty = writer

    def arguments(self, parser: ArgumentParser):
        pass

    def run(self, args) -> bool:
        pass
