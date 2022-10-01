import importlib
from typing import List

from flask import Flask
from rick.base import Di, Container, MapLoader
from rick.util.loader import load_class

from pokie.constants import DI_APP, DI_CONFIG, DI_SERVICE_MANAGER
from .module import BaseModule


class FlaskApplication:
    module_file_name = 'module'  # module class file name
    module_class_name = 'Module'  # default module class name

    def __init__(self, cfg: Container):
        self.di = Di()
        self.app = None
        self.modules = {} # app module list

        self.di.add(DI_CONFIG, cfg)
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
        self.di.add(DI_APP, self.app)

        # load modules
        self.modules = {}
        for name in module_list:
            cls = load_class("{}.{}.{}".format(name, self.module_file_name, self.module_class_name))
            if cls is None:
                raise RuntimeError("build(): cannot load module '{}' - Module() class not found".format(name))
            if not issubclass(cls, BaseModule):
                raise RuntimeError("build(): Class Module on '{}' must extend BaseModule".format(name))
            if name in self.modules.keys():
                raise ValueError("build(): Module named '{}' already exists".format(name))
            self.modules[name] = cls(self.di)

        # build service map
        svc_map = {}
        for name, m in self.modules.items():
            services = getattr(m, 'services', {})
            if type(services) is dict:
                svc_map.update(services)
            else:
                raise RuntimeError(
                    "build(): cannot load service map from module '{}'; attribute must be of type dict".format(name))
        # register service mapper
        self.di.add(DI_SERVICE_MANAGER, MapLoader(self.di, svc_map))

        # run factories
        for factory in factories:
            if type(factory) is str:
                # if factory is string, assume it is a path to a callable
                factory = load_class(factory)
            if not callable(factory):
                raise RuntimeError("build(): non-callable or non-existing factory")
            else:
                factory(self.di)

        # initialize modules
        for _, module in self.modules.items():
            module.build()

        return self.app
