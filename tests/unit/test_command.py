import io

from rick.base import Di
from rick.resource.console import ConsoleWriter

from pokie.constants import DI_TTY
from pokie.core.command import CliCommand


class ConcreteCommand(CliCommand):
    description = "test command"

    def run(self, args) -> bool:
        self.tty.write("hello world")
        return True


class TestCliCommand:
    def test_init_with_explicit_writer(self):
        di = Di()
        writer = ConsoleWriter(stdout=io.StringIO(), stderr=io.StringIO())
        cmd = ConcreteCommand(di, writer=writer)
        assert cmd.tty is writer

    def test_init_with_di_tty(self):
        di = Di()
        writer = ConsoleWriter(stdout=io.StringIO(), stderr=io.StringIO())
        di.add(DI_TTY, writer)
        cmd = ConcreteCommand(di)
        assert cmd.tty is writer

    def test_init_creates_default_writer(self):
        di = Di()
        cmd = ConcreteCommand(di)
        assert isinstance(cmd.tty, ConsoleWriter)

    def test_run_writes_to_tty(self):
        di = Di()
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = ConcreteCommand(di, writer=writer)
        result = cmd.run(None)
        assert result is True
        output = stdout.getvalue()
        assert "hello world" in output

    def test_arguments_is_noop(self):
        di = Di()
        cmd = ConcreteCommand(di)
        # arguments() should not raise
        from argparse import ArgumentParser

        parser = ArgumentParser()
        cmd.arguments(parser)

    def test_skipargs_default(self):
        assert ConcreteCommand.skipargs is False

    def test_description(self):
        assert ConcreteCommand.description == "test command"
