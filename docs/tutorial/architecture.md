# Pokie Architecture

Pokie promotes both **two-tier** and **three-tier** designs with heavy decoupling, in line with both 
**clean architecture** principles and **onion architecture** principles. The goal is to have only pure object records being carried
through the layers, such as [RickDB's DTO Objects](https://oddbit-project.github.io/rick_db/object_mapper/). Communication
is performed strictly top-down: each layer can only interect with the one immediately below,

A typical three-tier design has the following layers:

## Presentation layer

This is the level where Flask views are implemented, using class-based definitions; It is responsible for receiving requests, invoking dependencies, and
assembling responses; No specific business-related logic should reside here, adhering to the philosophy of "thin controllers".

As a default, these classes are instantiated as short-lived objects, and often only exist during the execution of a request, being 
destroyed afterwards. As such, all required initialization boilerplate must be as lightweight as possible. 

To override this behaviour and allow for long-lived view objects, please refer to the Flask documentation.  

## Service layer

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

## Data layer

The data layer provides basic data operations; this is often achieved by using [RickDb's Repository](https://oddbit-project.github.io/rick_db/repository/)
pattern, and DTO classes and objects. Due to the nature of the DTO objects (data-only objects with no business logic or internal state),
these can be passed upwards into the presentation layer.

Repositories can either be short-lived or long-lived, depending how they are use inside services; the most common approach
is to have long-lived repositories defined as properties within the service.

The instantiation of a repository is direct, but other mechanisms can be used if a greater degree of decoupling is required.
