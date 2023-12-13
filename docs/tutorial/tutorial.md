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

**Contents**:

- [Architecture](architecture.md)
- [Scaffolding](scaffolding.md)


## Initializing the application

To fully bootstrap the application, three components are required: the configuration container
(a *ShallowContainer* instance, [see below](#configuration)), the module list to be instantiated, and the factory list to be initialized.

It is recommended the bootstrap itself is built inside a factory function with the name *build_pokie()*; by encapsulating 
all the initialization within a single identified function, we can provide a clean application context to run unit 
tests.

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

>**Note:** The return *ShallowContainer* object from *Config.build()* will have **all keys in lowercase**, including the ones defined 
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


## Application factory: build_pokie()

Usage of the main application factory is not mandatory, but essential if unit tests are required. Unit testing often
requires the opposite strategy of a production application, in the sense that reusage and caching of objects should be
avoided completely. To ensure this, the factory encapsulates the complete bootstrap of the application, in such a way 
that can be called once per single test, ensuring that available internal resources are *not* reused. 

**build_pokie() -> Tuple[FlaskApplication, Flask]** 
Factory to build a pokie application and returns both the Pokie FlaskApplication object and the Flask object.

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

def build_pokie():
    # load configuration from ENV
    cfg = Config().build()
    
    # modules to load & initialize:
    # the internal auth module, and a custom-defined local module called 'my_module'
    modules = ['pokie.contrib.auth', 'my_module']
    
    # factories to run
    # the postgresql initializer, and the flask-login initializer
    factories = [PgSqlFactory, FlaskLogin, ]
    
    # build Pokie application
    pokie_app = FlaskApplication(cfg)
    # bootstrap Pokie application
    # the returned object is a Flask application
    flask_app = main.build(modules, factories)
    return pokie_app, flask_app
    
# main is reused for the cli wrapper
# app is often reused as the WSGI Flask object 
main, app = build_pokie()

# if it is a cli invocation
if __name__ == '__main__':
    # run the cli wrapper
    main.cli()
```

For development purposes, the application can be run directly:
```shell
$ python3 main.py runserver -d -r
 * Serving Flask app 'FlaskApplication' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
INFO:werkzeug: * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
INFO:werkzeug: * Restarting with watchdog (inotify)
WARNING:werkzeug: * Debugger is active!
INFO:werkzeug: * Debugger PIN: 354-883-950
```