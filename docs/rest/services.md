# REST services

Pokie provides several mixins to help with the implementation of REST services; These mixins rely on [DTO Objects](https://oddbit-project.github.io/rick_db/object_mapper/)
and [Repositories](https://oddbit-project.github.io/rick_db/repository/) to provide the common CRUD and listing 
functions.

## **pokie.rest.RestServiceMixin**

This mixin provides minimal CRUD functionality on top of a implementation-defined Repository; it can be used as a base implementation
when prototyping services, as it enables gradual replacement of existing base behaviours with more complex implementations
at a later stage in the development cycle. 

The mixin provides the following methods:

| Method                    | Result                            | Description                                                  |
|---------------------------|-----------------------------------|--------------------------------------------------------------|
| get(id_record)            | DTO Record if exists, None if not | Fetch a record by primary key                                |
| delete(id_record)         | None                              | Remove a record by primary key                               |
| insert(self, record)      | primary key value                 | Insert a new record                                          |
| update(id_record, record) | None                              | Update a record by primary key                               |
| exists(id_record)| True or False                     | Check if a record with the specified primary key exists      |
|list(...)*|tuple(total_count, rows)| Perform a listing operation based on the specified criteria  |

* list() uses [DbGrid](https://oddbit-project.github.io/rick_db/grid/) internally; check [REST Views](../http/rest.md) for more details. 

To make use of this mixin, just make sure your service inherits *pokie.rest.RestServiceMixin* and provides a 
a *repository* property returnung a valid Repository object:

```python
from pokie.constants import DI_DB
from rick.mixin import Injectable
from rick_db import Repository
from pokie.rest import RestServiceMixin
from my_fancy_app.dto import MyFancyRecord


class MyFancyService(Injectable, RestServiceMixin):

    @property
    def repository(self) -> Repository:
        return Repository(self.get_di().get(DI_DB), MyFancyRecord)
```

## **pokie.rest.RestService**

*RestService* is the service implementation used on [REST Views](../http/rest.md). It can also be used independently
to build custom services - just fill *record_class* with your desired DTO Record class 
(and optionally *repository_class* with your custom Repository class); If no repository is specified, *RestService*
will automatically build a generic *Repository* object based on *record_class*:

```python
from pokie.rest import RestService
from my_fancy_app.dto import MyFancyRecord
from my_fancy_app.repository import MyFancyRepository

class MyFancyService(RestService):
    # specify DTO Record class to use
    record_class = MyFancyRecord
    # specify a custom Repository class to use
    #repository_class = MyFancyRepository

```
*RestService* can also be used to build custom services in runtime - in fact, it is what *RestView* does internally - 
it builds a generic RestService and adds it to the Service Locator:

```python
from pokie.constants import DI_SERVICES
from pokie.rest import RestService
from pokie.http import PokieView
from my_fancy_app.dto import MyFancyRecord

class MyView(PokieView):
    
    def svc_custom(self) -> RestService:
        service_name = "my_custom_service_name"
        service_manager = self.di.get(DI_SERVICES)
        
        if not service_manager.contains(service_name):        
            # create new service object
            svc = RestService(self.di) 
            # set the DTO Record class
            svc.set_record_class(MyFancyRecord)
            # register the new service in the service manager    
            service_manager.register(service_name, svc)
            
            return svc
        
        return service_manager.get(service_name)
```

