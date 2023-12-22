# Pokie Views

Pokie extends on the class-based views on Flask, and offers additional features such as automatic request body unmarshall,
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

### Custom Response objects

PokieView responses are traditionally either **JsonResponse** or **CamelCaseJsonResponse** objects; however,
it is quite simple to override the default response class to use your own custom implementation - just
extend **pokie.http.ResponseRendererInterface**, and refer it in your view, using the **response_class** attribute: 

```python
from pokie.http import PokieView, ResponseRendererInterface


class HamburgerResponse(ResponseRendererInterface):

    def assemble(self, _app, **kwargs):
        # our custom Response only returns "hamburger"
        return "hamburger"


class CustomResponseView(PokieView):
    # custom response class to be used, intead of the default one
    response_class = HamburgerResponse

    def get(self):
        # just generate a response
        return self.success()
```

### CamelCase response

PokieView can, automatically, convert keys from the snake_case notation to camelCase before assembling the JSON response. This functionality
is provided by the *pokie.http.CamelCaseJsonResponse* class, and is controlled by the *PokieView.camel_case* attribute:

```python
from pokie.http import PokieView
from pokie_test.dto import CustomerRecord


class CamelCaseResponseView(PokieView):
    # enable automatic camelCasing of responses    
    camel_case = True

    def get(self):
        record = CustomerRecord(
            company_name="company_name",
            contact_name="contact_name",
            contact_title="contact_title",
            address="address"

        )
        return self.success(record)
```


Generated response:
```json
{
   "success":true,
   "data":{
      "address":"address",
      "companyName":"company_name",
      "contactName":"contact_name",
      "contactTitle":"contact_title"
   }
}
```


### Custom pre-dispatch hooks

Pre-dispatch hooks work as middlweware methods - they can be used to perform additional validations. If a given hook returns
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
