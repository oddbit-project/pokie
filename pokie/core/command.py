from abc import ABC
from argparse import ArgumentParser

from rick.base import Di
from rick.resource.console import ConsoleWriter
from rick.mixin import Injectable


class CliCommand(ABC, Injectable):
    description = "command description"

    def __init__(self, di: Di, writer=None):
        self.set_di(di)
        if not writer:
            writer = ConsoleWriter()
        self.tty = writer

    def arguments(self, parser: ArgumentParser):
        pass

    def run(self, args) -> bool:
        pass
