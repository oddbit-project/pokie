# Pokie Views

Pokie extends on the class-based views on Flask, and offers additional features such asautomatic request body unmarshall,
custom-named view methods (a-la Controllers), response helpers and authentication.

Using Pokie views is not mandatory; however, they are quite handy to implement REST-based APIs, and they provide extra
degrees of automation and JSON interaction.

## Using PokieView

**PokieView** is the base view class of Pokie. This class implements the following functionalities:

- optional automatic body deserialization and validation with a RequestRecord class;
- pre-dispatch hook system;
- json-first exception handler;
- json helpers;

### Body deserialization & validation

The request body can be automatically deserialized and validated for specific http methods (POST, PUT, PATCH) by specifying
a [RequestRecord](https://oddbit-project.github.io/rick/forms/requests/) class in the *request_class* class attribute. If the submitted data fails validation, a
[RequestRecord error response](https://oddbit-project.github.io/rick/forms/errors/) is returned. If validation is successful,
the handler method is called and the RequestRecord object instance can be accessed via *self.request* property.

Simple example with a custom RequestRecord class and a POST handler:

```python
from rick.form import RequestRecord, field
from pokie.http import PokieView

# JSON Request validation 
class FilmRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric'),
        'title': field(validators='required'),
        'description': field(validators=''),
        'releaseYear': field(validators='numeric'),
        'rating': field(validators=''),
        'lastUpdate': field(validators='required|iso8601'),
        'sinopse': field(validators='maxlen:2048'),
    }


class FilmView(PokieView):
    # use FilmRequest for automatic body deserialization and validation
    request_class = FilmRequest

    def post(self):
        
        print("submitted data:")
        #retrieve dict with all submitted values
        print(self.request.get_data())

        # return a standard JSON success response with code 200:
        # {"success":true,"message":""}
        return self.success() 
```

### Using custom dispatch hooks

Dispatch hooks work as middlweware methods - they can be used to perform additional validations. If a given hook returns
a **ResponseReturnValue**, the dispatch exits with the specified response. If a hook is run successfully, it should return None.

Example:
```python
from rick.form import RequestRecord, field
from pokie.http import PokieView

# JSON Request validation 
class FilmRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric'),
        'title': field(validators='required'),
        'description': field(validators=''),
        'releaseYear': field(validators='numeric'),
        'rating': field(validators=''),
        'lastUpdate': field(validators='required|iso8601'),
        'sinopse': field(validators='maxlen:2048'),
    }


class FilmView(PokieView):
    # use FilmRequest for automatic body deserialization and validation
    request_class = FilmRequest

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add hook method to the hook list
        self.dispatch_hooks.append('_my_hook')
    
    def _my_hook(self, method: str, *args: Any, **kwargs: Any) -> Optional[ResponseReturnValue]:
        """
        Custom hook to be executed on dispatch
        """
        if method == 'get':
            return self.error('We are blocking GET requests via dispatch hooks')
        return None
        
    def post(self):
        
        print("submitted data:")
        #retrieve dict with all submitted values
        print(self.request.get_data())

        # return a standard JSON success response with code 200:
        # {"success":true,"message":""}
        return self.success() 
```
