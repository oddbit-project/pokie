import os
import sys
import threading
import time
from typing import List

from flask import Flask
from rick.base import Di, Container, MapLoader
from rick.event import EventManager
from rick.mixin import Injectable, Runnable
from rick.util.loader import load_class
from rick.resource.console import ConsoleWriter

from pokie.constants import (
    DI_CONFIG,
    DI_SERVICES,
    DI_FLASK,
    DI_APP,
    DI_EVENTS,
    DI_TTY,
    DI_SIGNAL,
    CFG_HTTP_ERROR_HANDLER,
    DI_HTTP_ERROR_HANDLER,
)
import signal
from .signal_manager import SignalManager
from .middleware import ModuleRunnerMiddleware
from .module import BaseModule
from .command import CliCommand
from pokie.util.cli_args import ArgParser


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
        self.lock = threading.Lock()
        self.tty = ConsoleWriter()
        self.initialized = False
        self._built = False
        self._cli_initialized = False
        self._http_initialized = False

        self.pre_http_hooks = (
            []
        )  # list of hooks to run before initializing http operations
        self.pre_cli_hooks = (
            []
        )  # list of hooks to run before initializing cli operations
        self.pre_shutdown_hooks = (
            []
        )  # list of hooks to run during graceful shutdown

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
        if self._built:
            raise RuntimeError("build(): application has already been built")

        if not factories:
            factories = []

        self.app = Flask(type(self).__name__, static_folder=None)

        self.app.di = self.di
        self.di.add(DI_FLASK, self.app)

        # initialize signal manager
        self.di.add(DI_SIGNAL, SignalManager(self.di))

        # initialize TTY
        self.di.add(DI_TTY, self.tty)

        # run factories
        for factory in factories:
            if type(factory) is str:
                # if factory is string, assume it is a path to a callable
                factory = load_class(factory, raise_exception=True)
            if not callable(factory):
                raise RuntimeError("build(): non-callable or non-existing factory")
            else:
                factory(self.di)

        # load modules
        # Note: module load order is significant; system modules are loaded first, followed by
        # user modules in the order specified. Later modules can override services registered
        # by earlier modules, which is the intended mechanism for customization.
        self.modules = {}
        module_list = [*self.system_modules, *module_list]
        for name in module_list:
            cls = load_class(
                "{}.{}.{}".format(name, self.module_file_name, self.module_class_name),
                raise_exception=True,
            )
            if not issubclass(cls, BaseModule):
                raise RuntimeError(
                    "build(): Class Module on '{}' must extend BaseModule".format(name)
                )
            if name in self.modules.keys():
                raise ValueError(
                    "build(): Module named '{}' already exists".format(name)
                )
            self.modules[name] = cls(self.di)

        # build service map
        svc_map = {}
        for name, m in self.modules.items():
            services = getattr(m, "services", {})
            if type(services) is dict:
                svc_map.update(services)
            else:
                raise RuntimeError(
                    "build(): cannot load service map from module '{}'; attribute must be of type dict".format(
                        name
                    )
                )
        # register service mapper
        self.di.add(DI_SERVICES, MapLoader(self.di, svc_map))

        # parse events from modules
        evt_mgr = EventManager()
        for name, module in self.modules.items():
            module_events = getattr(module, "events", None)
            if isinstance(module_events, dict):
                for evt_name, evt_details in module_events.items():
                    if not isinstance(evt_details, dict):
                        raise RuntimeError(
                            "build(): invalid event structure for '{}' in module '{}'".format(evt_name, name)
                        )
                    for priority, handlers in evt_details.items():
                        if not isinstance(handlers, (list, tuple)):
                            raise RuntimeError(
                                "build(): event '{}' priority {} handlers must be a list in module '{}'".format(
                                    evt_name, priority, name
                                )
                            )
                        for handler in handlers:
                            evt_mgr.add_handler(evt_name, handler, int(priority))

        self.di.add(DI_EVENTS, evt_mgr)

        # register exception handler
        if self.cfg.has(CFG_HTTP_ERROR_HANDLER):
            handler = load_class(
                self.cfg.get(CFG_HTTP_ERROR_HANDLER), raise_exception=True
            )
            if not issubclass(handler, Injectable):
                raise RuntimeError(
                    "build(): HTTP_ERROR_HANDLER class does not extend Injectable"
                )
            # initialize & register handler
            handler = handler(self.di)
            self.di.add(DI_HTTP_ERROR_HANDLER, handler)

        self.app.wsgi_app = ModuleRunnerMiddleware(self.app.wsgi_app, self)
        self._built = True
        return self.app

    def register_pre_http_hook(self, f):
        """
        Register a hook to be executed during the init() of the webserver

        the hook must have the following interface:

        callable(app:FlaskApplication)

        :param f:
        :return:
        """
        self.pre_http_hooks.append(f)

    def register_pre_cli_hook(self, f):
        """
        Register a hook to be executed before any cli operation

        the hook must have the following interface:

        callable(app:FlaskApplication)

        :param f:
        :return:
        """
        self.pre_cli_hooks.append(f)

    def register_pre_shutdown_hook(self, f):
        """
        Register a hook to be executed during graceful shutdown

        the hook must have the following interface:

        callable(app:FlaskApplication)

        :param f:
        :return:
        """
        self.pre_shutdown_hooks.append(f)

    def shutdown(self):
        """
        Execute registered shutdown hooks for graceful cleanup
        """
        for fn in self.pre_shutdown_hooks:
            fn(self)

    def _build_modules(self):
        """
        Call build() on all registered modules. Idempotent.
        Must be called under self.lock for thread safety.
        """
        if not self.initialized:
            for _, module in self.modules.items():
                module.build(self)
            self.initialized = True

    def init(self):
        """Initialize modules and run pre-HTTP hooks. Called on first HTTP request."""
        if self._http_initialized:
            return
        with self.lock:
            if self._http_initialized:
                return
            self._build_modules()
            for fn in self.pre_http_hooks:
                fn(self)
            self._http_initialized = True

    def http(self, **kwargs):
        self.app.run(**kwargs)

    def cli_runner(self, command: str, args: list = None, **kwargs) -> int:
        # Note: module.build() is not called here because it is intended for HTTP
        # initialization (route registration). CLI commands access services via the DI
        # container, which is already populated during FlaskApplication.build().
        # Use pre_cli_hooks for any CLI-specific initialization.

        # run pre-cli hooks (once, on first cli_runner invocation)
        if not self._cli_initialized:
            for fn in self.pre_cli_hooks:
                fn(self)
            self._cli_initialized = True

        # either console or inline commands
        if args is None:
            args = []

        # extract writer before passing remaining kwargs to argument parser
        tty = kwargs.pop("writer", None) or self.di.get(DI_TTY)

        # parameter parser
        parser = ArgParser(**kwargs)

        # lookup handler
        for _, module in self.modules.items():
            if command in module.cmd.keys():
                handler = load_class(module.cmd[command], raise_exception=True)

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

                if handler.run(args):
                    return self.CLI_CMD_SUCCESS
                return self.CLI_CMD_FAILED

        # command not found
        tty.error("error executing '{}': command not found".format(command))
        return self.CLI_CMD_NOT_FOUND

    def cli(self, **kwargs):
        """
        Execute CLI commands
        :param kwargs: optional parameters for ArgumentParse
        :return:
        """
        # default command when no args detected
        command = "list"
        # extract command if specified
        if len(sys.argv) > 1:
            command = str(sys.argv[1])

        if "add_help" not in kwargs.keys():
            kwargs["add_help"] = False
        if "usage" not in kwargs.keys():
            kwargs["usage"] = "{} {} [OPTIONS...]".format(
                os.path.basename(sys.argv[0]), command
            )

        # exit code directly maps return codes
        exit(self.cli_runner(command, sys.argv[2:], **kwargs))

    def get_jobs(self) -> dict:
        result = {}
        for module_name, module in self.modules.items():
            jobs = getattr(module, "jobs", [])
            if len(jobs) > 0:
                result[module_name] = jobs
        return result

    def job_runner(self, single_run=False, silent=False):
        from .job_runner import JobRunner

        # prepare job list
        job_list = []
        for module_name, jobs in self.get_jobs().items():
            for job_name in jobs:
                if not silent:
                    self.tty.write("Preparing job  '{}'...".format(job_name))
                try:
                    job = load_class(job_name, raise_exception=True)
                except Exception:
                    if silent:
                        return False
                    raise
                if not issubclass(job, (Injectable, Runnable)):
                    if silent:
                        return False
                    raise RuntimeError(
                        "Class '{}' must implement Injectable, Runnable interfaces".format(
                            job_name
                        )
                    )
                job_list.append(job(self.di))

        # reverse job list so user module jobs run before system module jobs (e.g. IdleJob)
        job_list.reverse()

        runner = JobRunner(job_list, tty=self.tty, silent=silent)

        if single_run:
            runner.run_once(self.di)
        else:
            def abort_jobs(di, signal_no, stack_trace):
                self.shutdown()
                if not silent:
                    di.get(DI_TTY).write("\nCtrl+C pressed, exiting...")
                exit(0)

            runner.run_loop(
                self.di,
                signal_manager=self.di.get(DI_SIGNAL),
                abort_callback=abort_jobs,
            )
