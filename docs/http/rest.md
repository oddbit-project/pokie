# REST Views

Pokie provides several helpers to implement REST endpoints; one of them is the *RestView* class. This class
implements all the basic REST operations for CRUD operations on a given Record/Service. Service can either be the
generic *pokie.rest.RestService*,
or a custom service that implements *pokie.rest.RestServiceInterface*.

## Resource-based REST views - RestView

The *pokie.rest.RestView* provides the basic CRUD functionality for
a [RickDb Record](https://oddbit-project.github.io/rick_db/object_mapper/) class, effectively allowing automatic
creation of
CRUD endpoints for database objects, while maintaining a three-tier architectural design.

By default, RestView will attempt to create a *pokie.rest.RestService* instance, uniquely named by module and record
class. However,
if *service_name* is specified, the associated service will be used instead. Please note that services to be used with
the
*RestView* class need to extend from *pokie.rest.RestServiceMixin*.

RestView example:

```python
from pokie.rest import RestView
from rick.form import RequestRecord, field
from rick_db import fieldmapper


# DB Record class
@fieldmapper(tablename="country", pk="country_id", schema="public")
class CountryRecord:
    id = "country_id"
    country = "country"


# RequestRecord class
class CountryRequest(RequestRecord):
    fields = {
        "id": field(validators="id|numeric", bind="id"),
        "country": field(validators="required", bind="country")
    }


# REST view class
class CountryView(RestView):
    # RequestRecord class for body operations
    request_class = CountryRequest

    # Database Record class
    record_class = CountryRecord

    # allowed search fields to be used with the search variable
    search_fields = [CountryRecord.country]

    # optional custom service name to be used; if no service name is specified, an instance of
    # pokie.rest.RestService is automatically created
    # service_name = "my-service-name"

    # optional limit for default listing operations
    # if list_limit > 0, the specified value will be used as default limit for unbounded listing requests
    # list_limit = -1    
```

### Using RestView grid capabilities

By leveraging [DbGrid](https://oddbit-project.github.io/rick_db/grid/) capabilities through a [DbGridRequest](dbgridrequest.md) object, the RestView offers a set of
relevant features for advanced scenarios, such as server-side pagination, sorting and search.

the following url variables are available:

| Variable | Format                                                      | Example                         | Description                                                      |
|----------|-------------------------------------------------------------|---------------------------------|------------------------------------------------------------------|
| -        | -                                                           | /url                            | List all records, see response type below                        |
| offset   | <int>                                                       | /url?offset=5                   | List records starting at specified zero-based offset             |
| limit    | <int>                                                       | /url?limit=5                    | List limit amount of records                                     |
| search   | <string>                                                    | /url?search=foo                 | List search results for search expression                        |
| match    | field:value&#124;other_field:other_value[...&#124;field...] | /url?match=age:22&#124;gender:M | List records with exact match on the set of conditions presented |
| sort     | field:asc,field:desc                                        | /url?sort=name:asc,age:desc     | Sort records by specified conditions                             |

### Using offset, limit

Offset and limit behave like their SQL counterparts - zero-based integer numbers specifying an absolute value. They can
be combined to perform pagination:

```shell
# pagination with 10 records per page
/url?offset=10&limit=10
```

#### Using search

Search is performed in all fields specified in the view class *search_fields* attribute. The search is performed as
case-insensitive *%expression%*, allowing for matches inside strings. If multiple fields are specified in
*search_fields*,
the search is performed with OR concatenation - the result record list is the combination of all individual matches on
each
field.
Some of the internals of the search behaviour can be overridden by providing a custom *Service* class that
extends the *pokie.rest.RestServiceMixin* mixin and overrides the *list()* method implementation.

#### Using sort

Sort can be performed on multiple fields at once, and sort order can either be 'asc' or 'desc' in case-insensitive form.

#### Default operation and mixing multiple options

By default, a naked GET request to the listing endpoint will return all records; However, this may not be desirable when
the dataset size is bigger than a few hundred rows. It is possible to cap the default listing to a given number of rows
by changing the *list_limit* class attribute.

All or part of the specified options can be combined in a single request, to perform a server-side sorting & filtering
procedure.

Querying an endpoint with curl, using offset, limit, search and sort on the records:

```shell
$ curl -X GET -H 'Content-Type: application/json' http://127.0.0.1:5000/my_url?offset=10&limit=10&search=john&sort=name:desc
```

### Response format

All *RestView* operations return a variable JSON dataset with the following structure:

```json
{
  "total": 110,
  "items": [
    ...list
    of
    record
    objects...
  ]
}
```

Where **total** is the total amount of rows on the source dataset, ignoring offset and limit constraints, allowing the
implementation of server-side pagination.

## Registering routes

The traditional approach is to register the desired routes in the *build()* method of the *Module* class in *module.py*
of
your specific module, by using either traditional Flask routes or AutoRouter:

```python
(...)


class Module(BaseModule):
    (...)

    def build(self, parent=None):
        # get Flask application
        app = parent.app
        # register desired routes
        app.add_url_rule('/v1/my-rest-endpoint', methods=['GET', 'POST'],
                         view_func=MyRestView.as_view('my-rest-endpoint'))
        (...)
```

These routes are created when the module is loaded, so these operations are performed during the initialization of the
application. Please note that using Flask route decorators - while possible - it is not supported nor recommended.

RestView views can be added to the router using the traditional Flask approach; however, this process often envolves
needless creation of similar code. To simplify this process, the *pokie.http.AutoRouter* class can be used to
automate the registration of all endpoints at once:

```python
from pokie.http import AutoRouter
from pokie.rest import RestView
from rick.form import RequestRecord, field
from rick_db import fieldmapper


# DB Record class
@fieldmapper(tablename="country", pk="country_id", schema="public")
class CountryRecord:
    id = "country_id"
    country = "country"


# RequestRecord class
class CountryRequest(RequestRecord):
    fields = {
        "id": field(validators="id|numeric", bind="id"),
        "country": field(validators="required", bind="country")
    }


# REST view class
class CountryView(RestView):
    pass


(...)

# in our module's module.py:
(...)


class Module(BaseModule):
    (...)

    def build(self, parent=None):
        # register all routes automatically
        AutoRouter.resource(parent.app, "country", CountryView)
```

The following routes will be registered:

| Url                 | Method | Description      |
|---------------------|--------|------------------|
| /country            | GET    | List records     |
| /country            | POST   | Create record    |
| /country/:id_record | GET    | Get record by id |
| /country/:id_record | PUT    | Update record    |
| /country/:id_record | PATCH  | Update record    |
| /country/:id_record | DELETE | Delete record    | 

Please note that AutoRouter doesn't verify if the binding method receives the appropriate arguments, so always
make sure that the method signature is preserved when overriding it.

Classes may not implement all available methods for resource manipulation; AutoRouter will only define routes for
existing methods whose name match the resource operation - *get*, *post*, *put*, *delete*, or - alternatively -
the controller operation - *list*, *show*, *create*, *update*, *delete*.

### AutoRouter id_record type

By default, *AutoRouter* defines id_record as an **int** value; This can, however, be changed to any Flask supported
data type:

```python
(...)


# RequestRecord class
class CountryRequest(RequestRecord):
    fields = {
        "id": field(validators="required|maxlen:4", bind="id"),
        "country": field(validators="required", bind="country")
    }


# REST view class
class CountryView(RestView):
    pass


(...)
# in our module's module.py:
(...)


class Module(BaseModule):
    (...)

    def build(self, parent=None):
        # register all routes automatically, but id_record is of type string
        AutoRouter.resource(parent.app, "country", CountryView, "string")
```

## Controller-style REST views

Pokie also support Controller-style REST views - views where the handler of a given HTTP method can have a custom name.
Pokie's base view, *pokie.http.PokieView* already provides out-of-the-box support for these view types:

```python
# in our view file
from pokie.http import PokieView


# our Controller class:
class CustomerController(PokieView):

    # instead of get(self, id_customer:str=None), we can give it a custom name
    def view_customer(self, id_customer: str):
        """
        Get customer record
        :param id_customer: 
        :return: 
        """
        # attempt to fetch record from our existing customer service
        record = self.svc_customer().get_customer(id_customer)
        if not record:
            return self.not_found()

        # return record if exists
        return self.success(record)

    def svc_customer(self):
        return self.get_service(MY_CUSTOMER_SERVICE_CONSTANT)


(...)

# in our module's module.py:
(...)


class Module(BaseModule):
    (...)

    def build(self, parent=None):
        # register a custom route for the class method called "view_customer"
        app = parent.app
        app.add_url_rule(
            "/v1/customer/<string:id_customer>",
            methods=["GET"],
            view_func=CustomerController.view_method("view_customer"),
        )
```

### Using AutoRouter with Controllers

*pokie.http.AutoRouter* also provides automatic route registration for controller classes, if they implement the
appropriate methods:

| Method name | Method signature        | HTTP operation |
|-------------|-------------------------|----------------|
| list        | list(self)              | GET            |
| show        | show(self, id_record)   | GET            |
| create      | create(self)            | POST           |
| update      | update(self, id_record) | PUT, PATCH     |
| delete      | delete(self, id_record) | DELETE         |

The route registration will only map existing methods:

```python
# in our view file
from pokie.http import PokieView


# our Controller class:
class CustomerController(PokieView):

    # GET handler for customer record
    def show(self, id_record: str):
        """
        Get customer record
        :param id_record: 
        :return: 
        """
        # attempt to fetch record from our existing customer service
        record = self.svc_customer().get_customer(id_record)
        if not record:
            return self.not_found()

        # return record if exists
        return self.success(record)

    # GET handler for customer listing operations 
    def list(self):
        pass
    
    def svc_customer(self):
        return self.get_service(MY_CUSTOMER_SERVICE_CONSTANT)


(...)

# in our module's module.py:
(...)

class Module(BaseModule):
    (...)

    def build(self, parent=None):
        
        # register all available controller routes for class CustomerController:
        # /customer [GET] -> CustomerController.list()
        # /customer/<string:id_record> [GET] -> CustomerController.show()        
        AutoRouter.controller(parent.app, "customer", CustomerController, "string")
```
