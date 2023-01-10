# Fixtures

```python
from rick.base import Di
from rick.mixin import Injectable, Runnable

class CustomFixture(Injectable, Runnable):

    def run(self, di:Di):
        # do things here
        pass
```