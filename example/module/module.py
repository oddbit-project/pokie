from example.module.constants import SVC_SAMPLE
from pokie.core import BaseModule


class Module(BaseModule):
    name = "module"
    description = "Example module"

    # service map
    #
    # services are defined as {service_name: path_to_class}; The class must inherit the Injectable mixin
    # The service mapper will load by service name; be aware that service names must be unique, unless replacing existing
    # services
    #
    services = {
        SVC_SAMPLE: 'module.service.SampleService',
    }

    # cli command map
    #
    # cli commands are defined as {command: path_to_class}; The class must inherit from CliCommand
    # make sure the command names are unique; as with services, it is possible to replace commands
    #
    cmd = {
        'sample': 'module.cli.SampleCmd'
    }

    # events map
    #
    # events are refined as a two-level structure:
    # events = {
    #   'event_name': {
    #       numeric_priority: [path_to_handler, path_to_handler, ...]
    #   }
    # }
    #
    events = {
        'my_event_name': {
            10: ['module.event.handler.ExampleEventHandler', ]
        },
    }

    # jobs list
    #
    # jobs are tasks that are executed cooperatively as soon as possible; these tasks are useful for background operations
    # such as sending email or resizing images;
    #
    # jobs are defined by the full path name of the handler class; job classes must extend Injectable and Runnable mixins
    #
    jobs = []

    def build(self, parent=None):
        pass
