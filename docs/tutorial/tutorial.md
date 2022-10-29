# Pokie Tutorial

## Foreword

Pokie is built upon Dependency Injection and Resource Location. As such, dependencies are often specified by a full class
path string, instead of a direct import; coupling is inferred in runtime via provided configuration, instead of more
traditional approaches of using imports to provide dependencies. One of the main advantages of this approach is the
quasi-elimination of circular imports problem, and provides an elegant mechanism of overriding dependencies either at
load time or in runtime.

Pokie also makes heavy use of classes and namespaces, and often each class will reside in its own file; this requires more
discipline when scaffolding an application, and (sometimes) writing classes is more verbose than using more traditional
approaches. This is a calculated tradeoff by design, and not just a mere consequence of heavy pattern usage.

## Architecture

Pokie promotes both **two-tier** and **three-tier** designs with heavy decoupling, in line with both 
**clean architecture** principles and **onion architecture** principles. The goal is to have only pure object records being carried
through the layers, such as [RickDB's DTO Objects](https://oddbit-project.github.io/rick_db/object_mapper/). Communication
is performed strictly top-down: each layer can only interect with the one immediately below,

A typical three-tier design has the following layers:

### Presentation layer

This is the level where Flask views are implemented, using class-based definitions; It is responsible for receiving requests, invoking dependencies, and
assembling responses; No specific business-related logic should reside here, adhering to the philosophy of "thin controllers".

As a default, these classes are instantiated as short-lived objects, and often only exist during the execution of a request, being 
destroyed afterwards. As such, all required initialization boilerplate must be as lightweight as possible. 

To override this behaviour and allow for long-lived view objects, please refer to the Flask documentation.  

### Service layer

The service layer provides internal complex functionality to the presentation layer or for internal operation of the
application. Services are long-lived (by default atmost one instance created per service), but lazy-loaded - they are
only created if invoked for.

Services **cannot interact** with the Presentation layer; they are invoked (via service locator) from the Presentation layer; 
the service method signature may or may not be part of a formal interface, depending on design requirements.

Services **can interact** with other services, as well as with the data layer, immediately below. Also, it is quite common
to implement caching at the service level.

Keep in mind, services are - from a caller's perspective - stateless; they have no context of the application 
(eg. if its http or console, what is the current user session, etc), and all operations are - from a caller's perspective -
atomic. As such, if cache is implemented, it is up to the internal implementation of the service to ensure cache consistency
in such a way the service retains its stateless and context-less properties.

Services are invoked by a generic name, via a **MapLoader** object acting as a service locator. The service classes must
inherit the **Injectable** mixin. 

### Data layer

The data layer provides basic data operations; this is often achieved by using [RickDb's Repository](https://oddbit-project.github.io/rick_db/repository/)
pattern, and DTO classes and objects. Due to the nature of the DTO objects (data-only objects with no business logic or internal state),
these can be passed upwards into the presentation layer.

Repositories can either be short-lived or long-lived, depending how they are use inside services; the most common approach
is to have long-lived repositories defined as properties within the service.

The instantiation of a repository is direct, but other mechanisms can be used if a greater degree of decoupling is required.


## Application Scaffolding

Pokie applications are organized in modules - contained in folders, and a startup script usually called main.py:

```
my_project/
    project_module/
        __init__.py
        module.py  <- the module initialization class
    main.py        <- the startup script
```

## Initializing the application

To fully bootstrap the application, three components are required: the configuration container
(a *ShallowContainer* instance), the module list to be instantiated, and the factory list to be initialized.

The typical sequence of operations (both explicit and implicit) of a Pokie application is:

* load configuration; 
* build base Flask app; 
* load configured modules (instantiate Module objects only);
* build a service map and initialize the Service Manager;
* run factories defined in the factory list;
* parse event definitions from modules and build the Event Manager;
* initialize modules (by calling *build()* on each Module object);
* run appropriate CLI wrapper, or pass app variable to a WSGI server;

### Configuration

Pokie manages configuration using Rick's configuration resources - it supports both environment-variable based configuration
or file-based configuration using JSON format. Both are parsed into a *ShallowContainer* object.

#### Environment-based configuration

Environment-based configuration is a Docker-friendly mechanism to provide configurations; The configuration class extends
*EnvironmentConfig*, and when invoking build(), it attempts to read environment variables matching the existing **uppercase-named 
class attributes**. If a match is found, the default value is replaced. 

In addition, if the default value is an object of type *StrOrFile*, it will consider the specified existing value a
path to a file containing the actual value. Any *StrOrFile* attribute with a computed value (either default or injected
via environment variables) that starts with */* or *./* will be treated as a file to be read to determine the final value. 

**Note:** The return *ShallowContainer* object from *build()* will have **all keys in lowercase**, including the ones defined 
originally as uppercase. This allows the configuration class to have internal static configuration attributes that are
not injectable from environment variables.

Minimal Pokie environment-based configuration example:

```python
from rick.resource.config import EnvironmentConfig
from pokie.config.template import BaseConfigTemplate

# minimal Pokie environment-based configuration
# Pokie's defaults come from BaseConfigTemplate
class Config(EnvironmentConfig, BaseConfigTemplate):
    pass

# load configuration and return a ShallowContainer
cfg = Config().build()
```
#### File-based configuration

File-based configuration is comparatively simpler, as all values are read from the specified file. However, default values
for settings need also to exist on the file, resulting in more complex files.

Minimal Pokie file-based configuration example:

```python

from rick.resource.config import json_file

# load configuration from file and return a ShallowContainer
cfg = json_file('config.json')
```

config.json contents:
```json
{
  "modules": [],
  "use_auth": true,
  "auth_plugins": ["pokie.contrib.auth.plugin.DbAuthPlugin"],
  "auth_secret": "very_secret_key",
  "db_cache_metadata": false
}
```

### Module initialization

Bootstrapping a Pokie application requires a list of modules to be initialized; Each element of the list is a string with
a python class path for the module itself; Each module directory must then contain a *Module* class that inherits from
*BaseModule*, inside a file called *module.py*. This is the initialization class for a given module.

The list of modules to be initialized can also be provided via configuration setting, depending on the desired implementation.

### Factory initialization

Factories are assorted initializers for several purposes. One of them is to provide lazy loading mechanisms for
database connections or cache connections. The factory list is a list of direct classes (python classes, not strings).


## Minimal main.py example

The main.py script is usually a simple file, containing the previously mentioned components. In addition, it should
also provide the cli wrapper, to automatically also be able to execute cli operations. To enable this feature, just add
this to the bottom of the file:

```python
if __name__ == '__main__':
    main.cli()
```

A minimal  but complete main.py example:
```python
from rick.resource.config import EnvironmentConfig

from pokie.config.template import BaseConfigTemplate, PgConfigTemplate
from pokie.core import FlaskApplication
from pokie.core.factories.pgsql import PgSqlFactory


# base configuration
class Config(EnvironmentConfig, BaseConfigTemplate, PgConfigTemplate):
    pass


# load configuration from ENV
cfg = Config().build()

# modules to load & initialize:
# the internal auth module, and a custom-defined local module called 'my_module'
modules = ['pokie.contrib.auth', 'my_module']

# factories to run
# the postgresql initializer, and the flask-login initializer
factories = [PgSqlFactory, FlaskLogin, ]

# build Pokie application
main = FlaskApplication(cfg)
# bootstrap Pokie application
# the returned object is a Flask application
app = main.build(modules, factories)

# if it is a cli invocation
if __name__ == '__main__':
    # run the cli wrapper
    main.cli()
```

For development purposes, the application can be run directly:
```shell
$ python3 main.py runserver
 * Serving Flask app 'FlaskApplication' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
INFO:werkzeug: * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```