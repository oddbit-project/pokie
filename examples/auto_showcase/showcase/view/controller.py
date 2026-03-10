from flask import request

from pokie.http import PokieView, DbGridRequest
from pokie.constants import DI_DB
from rick_db import Repository
from showcase.dto import CustomerRecord


class CustomerController(PokieView):

    def list(self):
        db = self.di.get(DI_DB)
        repo = Repository(db, CustomerRecord)
        records = repo.fetch_all()
        return self.success({"total": len(records), "items": records})

    def show(self, id_record):
        db = self.di.get(DI_DB)
        repo = Repository(db, CustomerRecord)
        record = repo.fetch_pk(id_record)
        if record is None:
            return self.not_found()
        return self.success(record)
