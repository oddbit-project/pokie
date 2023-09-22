import os
import sys
from argparse import ArgumentParser
from typing import List
from collections import OrderedDict

from flask import Flask
from rick.base import Di, Container, MapLoader
from rick.event import EventManager
from rick.mixin import Injectable
from rick.util.loader import load_class
from rick.resource.console import ConsoleWriter

from pokie.constants import (
    DI_CONFIG,
    DI_SERVICES,
    DI_FLASK,
    DI_APP,
    DI_EVENTS,
    DI_TTY,
    DI_SIGNAL, CFG_HTTP_ERROR_HANLDER, DI_HTTP_ERROR_HANDLER,
)
from .module import BaseModule
from .command import CliCommand
from pokie.util.cli_args import ArgParser
from .signal import SignalManager


class FlaskApplication:
    CLI_CMD_SUCCESS = 0
    CLI_CMD_FAILED = 1
    CLI_CMD_NOT_FOUND = 2

    module_file_name = "module"  # module class file name
    module_class_name = "Module"  # default module class name

    system_modules = [
        "pokie.contrib.base",
    ]  # system modules to always be included

    def __init__(self, cfg: Container):
        self.di = Di()
        self.app = None
        self.modules = {}  # app module list

        self.di.add(DI_CONFIG, cfg)
        self.di.add(DI_APP, self)
        self.cfg = cfg

    def build(self, module_list: list, factories: List = None) -> Flask:
        """
        Build the application

        Factories is a list of optional callables to assemble functionality on top of Di, eg. database connection,
        cache, logging, etc. Factories are called *before* modules are initialized, to ensure all required dependencies
        are available

        :param module_list: list of module names to initialize
        :param factories: optional list of callables to be initialized with the application
        :return:
        """
        if not factories:
            factories = []

        self.app = Flask(type(self).__name__)
        self.app.di = self.di
        self.di.add(DI_FLASK, self.app)

        # initialize signal manager
        self.di.add(DI_SIGNAL, SignalManager(self.di))

        # initialize TTY
        self.di.add(DI_TTY, ConsoleWriter())

        # load modules
        self.modules = {}
        module_list = [*self.system_modules, *module_list]
        for name in module_list:
            cls = load_class(f"{name}.{self.module_file_name}.{self.module_class_name}")
            if cls is None:
                raise RuntimeError(
                    f"build(): cannot load module '{name}' - Module() class not found"
                )
            if not issubclass(cls, BaseModule):
                raise RuntimeError(f"build(): Class Module on '{name}' must extend BaseModule")
            if name in self.modules:
                raise ValueError(f"build(): Module named '{name}' already exists")
            self.modules[name] = cls(self.di)

        # build service map
        svc_map = {}
        for name, m in self.modules.items():
            services = getattr(m, "services", {})
            if type(services) is dict:
                svc_map.update(services)
            else:
                raise RuntimeError(
                    f"build(): cannot load service map from module '{name}'; attribute must be of type dict"
                )
        # register service mapper
        self.di.add(DI_SERVICES, MapLoader(self.di, svc_map))

        # run factories
        for factory in factories:
            if type(factory) is str:
                # if factory is string, assume it is a path to a callable
                factory = load_class(factory)
            if not callable(factory):
                raise RuntimeError("build(): non-callable or non-existing factory")
            else:
                factory(self.di)

        # parse events from modules
        evt_mgr = EventManager()
        for module in self.modules.values():
            module_events = getattr(module, "events", None)
            if isinstance(module_events, dict):
                for evt_name, evt_details in module_events.items():
                    for priority, handlers in evt_details.items():
                        for handler in handlers:
                            evt_mgr.add_handler(evt_name, handler, int(priority))

        self.di.add(DI_EVENTS, evt_mgr)

        # register exception handler
        if self.cfg.has(CFG_HTTP_ERROR_HANLDER):
            handler = load_class(self.cfg.get(CFG_HTTP_ERROR_HANLDER), True)
            if not issubclass(handler, Injectable):
                raise RuntimeError("build(): HTTP_ERROR_HANDLER class does not extend Injectable")
            # initialize & register handler
            handler = handler(self.di)
            self.di.add(DI_HTTP_ERROR_HANDLER, handler)

        # initialize modules
        for module in self.modules.values():
            module.build(self)

        return self.app

    def http(self, **kwargs):
        self.app.run(**kwargs)

    def cli_runner(self, command: str, args: list = None, **kwargs) -> int:
        # either console or inline commands
        if args is None:
            args = []

        # parameter parser
        parser = ArgParser(**kwargs)

        tty = kwargs["writer"] if "writer" in kwargs else ConsoleWriter()
        # lookup handler
        for _, module in self.modules.items():
            if command in module.cmd.keys():
                handler = load_class(module.cmd[command])
                if not handler:
                    raise RuntimeError(f"cli(): handler class '{module.cmd[command]}' not found")
                if not issubclass(handler, CliCommand):
                    raise RuntimeError(
                        "cli(): command handler does not extend CliCommand"
                    )
                handler = handler(self.di, writer=tty)  # type: CliCommand
                if not handler.skipargs:  # skipargs controls usage of argparser
                    handler.arguments(parser)
                    args = parser.parse_args(args)
                    if parser.failed:
                        # invalid/insufficient args
                        tty.error(parser.error_message)
                        parser.print_help(tty.stderr)
                        return self.CLI_CMD_FAILED
                else:
                    # skipargs is true, all argparsing is ignored
                    # this allow for custom cli arg handling
                    args = None

                return self.CLI_CMD_SUCCESS if handler.run(args) else self.CLI_CMD_FAILED
        # command not found
        tty.error(f"error executing '{command}': command not found")
        return self.CLI_CMD_NOT_FOUND

    def cli(self, **kwargs):
        """
        Execute CLI commands
        :param kwargs: optional parameters for ArgumentParse
        :return:
        """
        command = str(sys.argv[1]) if len(sys.argv) > 1 else "list"
        if "add_help" not in kwargs.keys():
            kwargs["add_help"] = False
        if "usage" not in kwargs.keys():
            kwargs["usage"] = f"{os.path.basename(sys.argv[0])} {command} [OPTIONS...]"

        # exit code directly maps return codes
        exit(self.cli_runner(command, sys.argv[2:], **kwargs))
