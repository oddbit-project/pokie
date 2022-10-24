from rick.base import Registry
from rick.mixin import Translator


class DataType:

    def field(self, data:ColumnRecord):
        pass

# Validator registry
registry = Registry(DataType)
