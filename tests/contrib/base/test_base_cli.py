import io
from argparse import Namespace

from rick.resource.console import ConsoleWriter

import pokie
from pokie.contrib.base.cli.base import VersionCmd, ListCmd, HelpCmd


class TestVersionCmd:
    def test_outputs_version(self, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = VersionCmd(pokie_di, writer=writer)
        result = cmd.run(None)
        assert result is True
        output = stdout.getvalue()
        assert pokie.get_version() in output


class TestListCmd:
    def test_outputs_commands(self, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = ListCmd(pokie_di, writer=writer)
        result = cmd.run(None)
        assert result is True
        output = stdout.getvalue()
        assert "available commands" in output.lower()


class TestHelpCmd:
    def test_existing_command(self, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = HelpCmd(pokie_di, writer=writer)
        args = Namespace(command="version")
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        assert "version" in output.lower()

    def test_nonexistent_command(self, pokie_di):
        stdout = io.StringIO()
        stderr = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=stderr)
        cmd = HelpCmd(pokie_di, writer=writer)
        args = Namespace(command="nonexistent_command_xyz")
        result = cmd.run(args)
        assert result is False
