from example.module.constants import SVC_SAMPLE
from pokie.core import BaseModule


class Module(BaseModule):
    # internal module name, must be unique
    name = "module"

    # internal module description
    description = "Example module"

    # service map
    #
    # this map registers existing module services, and makes them available to the application. Services are lazy-loaded
    # upon first invocation, to reduce overhead. A service class must inherit the Injectable mixin.
    #
    # The service mapper will load services by service name; As such, service names should be unique, unless the goal
    # is to explicitly override already-registered services
    #
    services = {
        # service entries are defined as {'service_name': 'path_to_class'}
        SVC_SAMPLE: 'module.service.SampleService',
    }

    # cli command map
    #
    # this map registers existing cli commands exposed by the module. Cli commands are classes that inherit from
    # CliCommand. Cli command names should be unique, unless the goal is to explicitly override existing commands
    #
    cmd = {
        # cli commands are defined as {'command': 'path_to_class'}
        'sample': 'module.cli.SampleCmd'
    }

    # events map
    #
    # Pokie has a concept similar to signals in other framework., but with different capabilities, called Events. Events
    # are classes that extend from EventHandler, and implement a method with the name of the event. Event handler objects
    # are short-lived - they are created upon dispatched of a given event, and de-referenced afterwards.
    #
    # Events have a priority number - handler execution follows the priority number in descending order (lower numbers get
    # executed first)
    #
    # Events also have optional in and out objects, typically used for dictionary composition. A common use case is to add
    # extra information to the response generated on a given information, such as login
    #
    # Event names are unique strings that identify the event; there is no specific requirements for naming, but common
    # convention suggests the usage of snakecase (eg. some_event).
    #
    #
    # events are refined as a two-level structure, containing zero or more events, and then handlers and priorities:
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

    # worker jobs list
    #
    # jobs are tasks that are executed continuously and cooperatively, in a closed loop; their purpose is to execute
    # background operations such as sending emails or resizing images. What makes them different from cron approaches
    # is their continuous execution - there is an idle job with a default 15s pause, and then all other jobs are run
    # sequentially, in a closed loop. If a given job takes too much time to execute, it will delay subsequent jobs, so
    # this approach may not fit all workloads.
    #
    # Jobs are long-lived objects whose class must extend Injectable and Runnable mixins.
    # The job list is a list of strings with the full path for each job class, similar to other existing referencing structures
    #
    jobs = [
        # 'full.path.to.job.class'
    ]

    # fixture class list
    #
    # fixtures are objects that are run only once; They can be used to load initial/default values or to perform non-trivial
    # database operations, such as data migrations
    #
    fixtures = [
        # 'full.path.to.fixture.class
    ]

    def build(self, parent=None):
        # This method is called when modules are initialized; At this point, all other dependencies have already been
        # initialized, including the Service Manager, Event Manager and even registered factories
        #
        # All Flask-related routing calls should reside here
        pass
