from rick.base import Di
from rick.mixin import Injectable
from rick_db import Repository

from pokie.constants import DI_DB
from pokie.rest import RestServiceMixin
from showcase.dto import ProductRecord


class ProductService(Injectable, RestServiceMixin):
    def __init__(self, di: Di):
        super().__init__(di)

    @property
    def repository(self) -> Repository:
        return Repository(self.get_di().get(DI_DB), ProductRecord)
