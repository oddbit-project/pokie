# Extending Views

PokieView functionality can be extended in several ways, either by using pre-dispatch hooks, subclassing or by using
Mixins.

## Using Hooks

Hooks are methods that are called before performing the dispatch of a given request, and they are maintained in two
list attributes - *PokieView.dispatch_hooks* and *PokieView.internal_hooks*. Because when a request is received these methods
are called in order sequence by name, by using two lists we guarantee that expensive system hooks - such as automatic body 
serialization - are postponed to execute after all application hooks, such as authentication.

All hooks must use the interface *(method:str, \*args: t.Any, \*\*kwargs: t.Any) -> Optional[ResponseReturnValue]* and
if they return a value different than *None*, the dispatch is immediately aborted and that value is used as a *Response*.

There is no specific naming nomenclature for hooks, but due to their status as protected functions, their name should start
with underscore ("_").

## Hooks in subclasses 

Adding custom hooks to subclasses is quite simple - just override the __init__() method, add your hooks, and fill
the appropriate lists with their names:

```python
from pokie.constants import DI_CONFIG
from pokie.http import PokieView
from flask import request
from typing import Any, Optional
from flask.typing import ResponseReturnValue

class TokenAuthView(PokieView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # get hardcoded auth key from a config value
        self.auth_token = self.di.get(DI_CONFIG).GET("auth_token", None)
        # add auth hook 
        self.dispatch_hooks.append("_hook_token_auth")

    def _hook_token_auth(self, method: str, *args: Any, **kwargs: Any) -> Optional[ResponseReturnValue]:
        if not self.auth_token:
            # no token defined, allow access
            return None
        
        if "x-access-key" in request.headers:
             if self.auth_token == request.headers['x-access-token']:
                 # valid auth token 
                 return None
             
        # Invalid auth token            
        return self.forbidden()
```


## Hooks in Mixins

Pokie also supports Mixin initializers, that can be used to implement specific hook functionality. These initializers
are called by name at the end of the *__init__()* function. These initializer methods can have any valid name and
follow *(\*\*kwargs)* as an interface:

```python
from pokie.http import PokieView
from flask import request
from typing import Any, Optional
from flask.typing import ResponseReturnValue

class TokenAuthMixin:
    
    def init_auth(self, **kwargs):
        self.dispatch_hooks.append("_hook_token_auth")        
    
    def _hook_token_auth(self, method: str, *args: Any, **kwargs: Any) -> Optional[ResponseReturnValue]:
        if not self.auth_token:
            # no token defined, allow access
            return None
        
        if "x-access-key" in request.headers:
             if self.auth_token == request.headers['x-access-token']:
                 # valid auth token 
                 return None
             
        # Invalid auth token            
        return self.forbidden()


# declare a class using the mixin
class MyView(PokieView, TokenAuthMixin):
    # Add the Mixin initializer name to be called on __init__()
    init_methods = ["init_auth",]


```