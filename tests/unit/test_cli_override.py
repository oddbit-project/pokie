import io
import threading

from rick.base import Di
from rick.resource.console import ConsoleWriter

from pokie.constants import DI_APP, DI_TTY
from pokie.contrib.base.cli.base import BaseCommand, HelpCmd, ListCmd
from pokie.core import CliCommand
from pokie.core.application import FlaskApplication
from pokie.core.module import BaseModule

HERE = "tests.unit.test_cli_override"

# commands append their tag here when run, so a test can assert WHICH class the
# dispatcher picked rather than only that something succeeded
EXECUTED = []


class RecordingCmd(CliCommand):
    tag = "recording"
    result = True

    def run(self, args) -> bool:
        EXECUTED.append(self.tag)
        return self.result


# NOTE: no description here may contain a command NAME — one of the tests below
# counts occurrences of "db:update" in the rendered listing.
class SystemDbUpdateCmd(RecordingCmd):
    description = "the update command as declared by the system module"
    tag = "system"


class AppDbUpdateCmd(RecordingCmd):
    description = "the update command as declared by the application module"
    tag = "app"


class SystemListCmd(RecordingCmd):
    description = "a command only the system module declares"
    tag = "system-list"


class AppCustomCmd(RecordingCmd):
    description = "a command only the application module declares"
    tag = "app-custom"


class FailingCmd(RecordingCmd):
    description = "a command that reports failure"
    tag = "failing"
    result = False


class SystemModule(BaseModule):
    name = "system"
    description = "a system module, always loaded first"
    cmd = {
        "db:update": HERE + ".SystemDbUpdateCmd",
        "list": HERE + ".SystemListCmd",
    }


class AppModule(BaseModule):
    name = "app"
    description = "an application module"
    cmd = {
        "db:update": HERE + ".AppDbUpdateCmd",
        "custom": HERE + ".AppCustomCmd",
    }


class FailingModule(BaseModule):
    name = "failing"
    description = "declares a command that returns False"
    cmd = {"boom": HERE + ".FailingCmd"}


def _writer():
    return ConsoleWriter(stdout=io.StringIO(), stderr=io.StringIO())


def _app(*modules) -> FlaskApplication:
    """An application with just enough state to resolve and run cli commands."""
    app = FlaskApplication.__new__(FlaskApplication)
    app.modules = {m.name: m.__new__(m) for m in modules}
    app.di = Di()
    app.lock = threading.Lock()
    app.pre_cli_hooks = []
    app._cli_initialized = True
    app.di.add(DI_APP, app)
    app.di.add(DI_TTY, _writer())
    return app


class TestCommandResolution:
    def test_later_module_overrides_earlier(self):
        # system_modules are prepended to the module list, so overriding one of
        # their commands is only possible if the later module wins
        app = _app(SystemModule, AppModule)
        assert app.resolve_command("db:update") == HERE + ".AppDbUpdateCmd"

    def test_commands_that_are_not_overridden_are_kept(self):
        app = _app(SystemModule, AppModule)
        assert app.resolve_command("list") == HERE + ".SystemListCmd"
        assert app.resolve_command("custom") == HERE + ".AppCustomCmd"

    def test_unknown_command_resolves_to_none(self):
        app = _app(SystemModule, AppModule)
        assert app.resolve_command("no:such:command") is None

    def test_command_map_holds_one_entry_per_name(self):
        app = _app(SystemModule, AppModule)
        cmd_map = app.get_command_map()
        assert cmd_map["db:update"] == HERE + ".AppDbUpdateCmd"
        assert len(cmd_map) == 3

    def test_precedence_follows_load_order(self):
        # reversing the load order reverses the winner: precedence is a property
        # of the order, not of the modules
        app = _app(AppModule, SystemModule)
        assert app.resolve_command("db:update") == HERE + ".SystemDbUpdateCmd"

    def test_no_modules(self):
        app = _app()
        assert app.get_command_map() == {}
        assert app.resolve_command("list") is None


class TestCommandDispatch:
    def setup_method(self):
        EXECUTED.clear()

    def test_the_overriding_command_is_the_one_that_runs(self):
        # the point of the whole change: resolution and execution must agree
        app = _app(SystemModule, AppModule)
        assert app.cli_runner("db:update", [], writer=_writer()) == app.CLI_CMD_SUCCESS
        assert EXECUTED == ["app"]

    def test_dispatch_follows_load_order(self):
        app = _app(AppModule, SystemModule)
        assert app.cli_runner("db:update", [], writer=_writer()) == app.CLI_CMD_SUCCESS
        assert EXECUTED == ["system"]

    def test_commands_that_are_not_overridden_still_dispatch(self):
        app = _app(SystemModule, AppModule)
        app.cli_runner("list", [], writer=_writer())
        app.cli_runner("custom", [], writer=_writer())
        assert EXECUTED == ["system-list", "app-custom"]

    def test_unknown_command_reports_not_found(self):
        app = _app(SystemModule, AppModule)
        writer = _writer()
        assert (
            app.cli_runner("no:such:command", [], writer=writer)
            == app.CLI_CMD_NOT_FOUND
        )
        assert EXECUTED == []
        assert "command not found" in writer.stderr.getvalue()

    def test_a_command_returning_false_reports_failure(self):
        app = _app(FailingModule)
        assert app.cli_runner("boom", [], writer=_writer()) == app.CLI_CMD_FAILED
        assert EXECUTED == ["failing"]

    def test_single_module_is_unaffected(self):
        # the common case: one module, one declaration, nothing to override
        app = _app(SystemModule)
        assert app.cli_runner("db:update", [], writer=_writer()) == app.CLI_CMD_SUCCESS
        assert EXECUTED == ["system"]


class TestListingAgreesWithExecution:
    def setup_method(self):
        EXECUTED.clear()

    def test_base_command_map_is_the_application_map(self):
        app = _app(SystemModule, AppModule)
        cmd = BaseCommand(app.di, writer=_writer())
        assert cmd.get_cmd_map() == app.get_command_map()

    def test_help_describes_the_class_that_would_run(self):
        # before, help/list read the LAST declaration and cli_runner ran the FIRST
        app = _app(SystemModule, AppModule)
        writer = _writer()
        assert HelpCmd(app.di, writer=writer).run(_Args("db:update")) is True
        assert AppDbUpdateCmd.description in writer.stdout.getvalue()
        assert SystemDbUpdateCmd.description not in writer.stdout.getvalue()

    def test_list_shows_an_overridden_command_once(self):
        app = _app(SystemModule, AppModule)
        writer = _writer()
        assert ListCmd(app.di, writer=writer).run(None) is True
        out = writer.stdout.getvalue()
        assert out.count("db:update") == 1
        assert AppDbUpdateCmd.description in out
        assert SystemDbUpdateCmd.description not in out

    def test_every_listed_command_resolves_to_the_listed_class(self):
        app = _app(SystemModule, AppModule, FailingModule)
        cmd = BaseCommand(app.di, writer=_writer())
        for name, path in cmd.get_cmd_map().items():
            assert app.resolve_command(name) == path


class _Args:
    """Stand-in for the parsed argparse namespace HelpCmd expects."""

    def __init__(self, command):
        self.command = command
