from typing import List

from rick.form import RequestRecord
from flask import request
from .helpers import ParseListError, parse_list_parameters
from pokie.rest import RestService
from pokie.constants import DI_SERVICE_MANAGER
from inspect import isclass


class RestMixin:
    request_class = None  # type: RequestRecord
    record_class = None
    search_fields = None  # type: List
    svc_name = None

    def get(self, id_record=None):
        """
        Read single record by id
        :param id_record:
        :return:
        """
        if id_record is None:
            return self.list()

        record = self.svc.get(id_record)
        if record is None:
            return self.not_found()

        return self.success(record)

    def list(self):
        """
        Query records
        :return:
        """
        search_fields = self.search_fields if self.search_fields is not None else []
        text, match, limit, offset, sort = parse_list_parameters(request.args, self.record_class)
        try:
            count, data = self.svc.list(
                search_fields=search_fields,
                search_text=text,
                match_fields=match,
                limit=limit,
                offset=offset,
                sort_fields=sort)
            result = {
                'total': count,
                'rows': data
            }
            return self.success(result)
        except ParseListError as e:
            return self.error(str(e))

    def post(self):
        """
        Create Record
        :return:
        """
        data = request.json
        if data is None or len(data) == 0:
            return self.empty_body()

        req = self.request_factory
        if not req.is_valid(request.json):
            return self.request_error(req)

        record = req.bind(self.record_class)
        self.svc.insert(record)
        return self.success()

    def put(self, id_record):
        """
        Update Record
        :return:
        """
        data = request.json
        if data is None or len(data) == 0:
            return self.empty_body()

        if not self.svc.exists(id_record):
            return self.not_found()

        req = self.request_factory
        if not req.is_valid(request.json):
            return self.request_error(req)

        record = req.bind(self.record_class)
        self.svc.update(id_record, record)
        return self.success()

    def delete(self, id_record):
        """
        delete Record by id
        :param id_record:
        :return:
        """
        if not self.svc.exists(id_record):
            return self.not_found()

        self.svc.delete(id_record)
        return self.success()

    @property
    def request_factory(self) -> RequestRecord:
        if isclass(self.request_class):
            return self.request_class()
        return self.request_class

    @property
    def svc(self) -> RestService:
        mgr = self.di.get(DI_SERVICE_MANAGER)
        if self.svc_name is None:
            svc_name = "svc.rest.{}.{}".format(self.__module__,
                                               str(self.record_class.__name__).replace('Record', '', 1))
            if mgr.contains(svc_name):
                return mgr.get(svc_name)

            # register new service that relies on a RestService instance
            mgr.add(svc_name, 'pokie.rest.RestService')
            # get new service to patch it
            svc = mgr.get(svc_name)
            # patch it
            svc.set_record_class(self.record_class)
            return svc

        svc = mgr.get(self.svc_name)
        if not isinstance(svc, RestService):
            raise RuntimeError("Service '{}' does not implement RestService mixin")
        return svc
