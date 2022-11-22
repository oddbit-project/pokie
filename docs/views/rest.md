# REST Views

Pokie provide several helpers to implement REST endpoints; one of them is the *RestMixin* mixin. This class extension
implements all the basic REST operations for CRUD operations on a given Record/Service. Service can either be the generic *pokie.rest.RestService*,
or a custom service that implements *pokie.rest.RestServiceInterface*.

The RestMixin provides the basic CRUD functionality for a [RickDb Record](https://oddbit-project.github.io/rick_db/object_mapper/) class, effectively allowing automatic creation of
CRUD endpoints for database objects, while maintaining a three-tier architectural design.

By default, RestMixin will attempt to create a *pokie.rest.RestService* instance, uniquely named by module and record class. However,
if *service_name* is specified, the associated service will be used instead. Please note that services to be used with the
*RestMixin* class need to extend from *pokie.rest.RestServiceMixin*.

RestMixin example:
```python
from pokie.http import PokieView
from pokie.http.rest import RestMixin
from rick.form import RequestRecord, field
from rick_db import fieldmapper

# DB Record class
@fieldmapper(tablename='country', pk='country_id', schema='public')
class CountryRecord:
    id = 'country_id'
    country = 'country'

# RequestRecord class
class CountryRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric', bind='id'),
        'country': field(validators='required', bind='country')
    }

# REST view class
class CountryView(PokieView, RestMixin):
    
    # RequestRecord class for body operations
    request_class = CountryRequest
    
    # Database Record class
    record_class = CountryRecord
    
    # allowed search fields to be used with the search variable
    search_fields = [CountryRecord.country]

    # optional custom service name to be used; if no service name is specified, an instance of
    # pokie.rest.RestService is automatically created
    #service_name = 'my-service-name'
    
    # optional limit for default listing operations
    # if list_limit > 0, the specified value will be used as default limit for unbounded listing requests
    #list_limit = -1    
```

## Registering routes

RestMixin views can be added to the router using the traditional Flask approach; however, this process often envolves
needless creation of similar code. To simplify this process, the *pokie.http.route_resource()* helper can be used to
automate the registration of all endpoints at once:

```python
from pokie.http import PokieView
from pokie.http.rest import RestMixin
from rick.form import RequestRecord, field
from rick_db import fieldmapper

# DB Record class
@fieldmapper(tablename='country', pk='country_id', schema='public')
class CountryRecord:
    id = 'country_id'
    country = 'country'

# RequestRecord class
class CountryRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric', bind='id'),
        'country': field(validators='required', bind='country')
    }

# REST view class
class CountryView(PokieView, RestMixin):
    pass

(...)
# register all routes automatically
route_resource(app, 'country', CountryView)
```
The following routes will be registered:

|Url| Method | Description      |
|---|--------|------------------|
|/country| GET    | List records     |
|/country| POST   | Create record    |
|/country/:id| GET    | Get record by id |
|/country/:id| PUT    | Update record    |
|/country/:id| DELETE | Delete record    | 


## Using RestMixin grid capabilities

By leveraging [DbGrid](https://oddbit-project.github.io/rick_db/grid/) capabilities, the RestMixin offers a set of relevant
features for advanced scenarios, such as server-side pagination, sorting and search.

the following url variables are available:

|Variable| Format                                                      | Example                         | Description                                          |
|---|-------------------------------------------------------------|---------------------------------|------------------------------------------------------|
| - | -                                                           | /url                            | List all records, see response type below            |
|offset| <int>                                                       | /url?offset=5                   | List records starting at specified zero-based offset |
|limit| <int>                                                       | /url?limit=5                    | List limit amount of records                         |
|search| <string>                                                    | /url?search=foo                 | List search results for search expression            |
|match| field:value&#124;other_field:other_value[...&#124;field...] | /url?match=age:22&#124;gender:M |List records with exact match on the set of conditions presented|
|sort|field:asc,field:desc|/url?sort=name:asc,age:desc| Sort records by specified conditions|

### Using offset, limit

Offset and limit behave like their SQL counterparts - zero-based integer numbers specifying an absolute value. They can
be combined to perform pagination:

```shell
# pagination with 10 records per page
/url?offset=10&limit=10
```

### Using search

Search is performed in all fields specified in the view class *search_fields* attribute. The search is performed as 
case-insensitive *%expression%*, allowing for matches inside strings. If multiple fields are specified in *search_fields*,
the search is performed with OR concatenation - the result record list is the combination of all individual matches on each 
field.
Some of the internals of the search behaviour can be overridden by providing a custom *Service* class that
extends the *pokie.rest.RestServiceMixin* mixin and overrides the *list()* method implementation.


### Using sort

Sort can be performed on multiple fields at once, and sort order can either be 'asc' or 'desc' in case-insensitive form.


### Default operation and mixing multiple options

By default, a naked GET request to the listing endpoint will return all records; However, this may not be desirable when
the dataset size is bigger than a few hundred rows. It is possible to cap the default listing to a given number of rows
by changing the *list_limit* class attribute.

All or part of the specified options can be combined in a single request, to perform a server-side sorting & filtering procedure.

Querying an endpoint with curl, using offset, limit, search and sort on the records:
```shell
$ curl -X GET -H 'Content-Type: application/json' http://127.0.0.1:5000/my_url?offset=10&limit=10&search=john&sort=name:desc
```


## Response format

All *RestMixin* operations return a variable JSON dataset with the following structure:

```json
{
  "total": 110,
  "rows": [
    ...list
    of
    record
    objects...
  ]
}
```
Where **total** is the total amount of rows on the source dataset, ignoring offset and limit constraints, allowing the
implementation of server-side pagination.

