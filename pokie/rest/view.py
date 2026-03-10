from typing import List

from flask import request

from flask.typing import ResponseReturnValue
from pokie.http import DbGridRequest, PokieView
from pokie.rest import RestService, RestServiceMixin
from pokie.constants import DI_SERVICES, HTTP_BADREQ, HTTP_INTERNAL_ERROR


class RestView(PokieView):
    """
    WARNING: RestView extends PokieView, which is unauthenticated by default.
    All auto-generated endpoints are publicly accessible unless you subclass
    PokieAuthView instead, or provide a PokieAuthView-based class.
    """

    record_class = None
    search_fields = None  # type: List
    service_name = None
    list_limit = -1
    camel_case = False

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
        dbgrid_request = DbGridRequest(
            self.record_class, use_camel_case=self.camel_case
        )

        if not dbgrid_request.is_valid(request.args):
            return self.request_error(dbgrid_request)
        try:
            count, data = self.svc.list(
                **dbgrid_request.dbgrid_parameters(self.list_limit, search_fields)
            )
            result = {"total": count, "items": data}
            return self.success(result)
        except Exception as e:
            self.logger.exception(e)
            return self.error("internal error", code=HTTP_INTERNAL_ERROR)

    def post(self):
        """
        Create Record
        :return:
        """
        record = self.request.bind(self.record_class)
        result = self.svc.insert(record)
        return self.success({"id": result})

    def put(self, id_record):
        """
        Update Record
        :return:
        """
        if not self.svc.exists(id_record):
            return self.not_found()
        record = self.request.bind(self.record_class)
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

    def exception_handler(self, e) -> ResponseReturnValue:
        if e is not None:
            self.logger.exception(e)
        return self.error("bad request", code=HTTP_BADREQ)

    @property
    def svc(self) -> RestService:
        mgr = self.di.get(DI_SERVICES)
        if not self.service_name:
            if self.record_class is None:
                raise RuntimeError("RestView: record_class or service_name must be set")
            svc_name = "svc.rest.{}.{}".format(
                self.__module__,
                str(self.record_class.__name__).replace("Record", "", 1),
            )
            if mgr.contains(svc_name):
                return mgr.get(svc_name)

            # build service
            svc = RestService(self.di)
            svc.set_record_class(self.record_class)

            # register it in the service manager
            mgr.register(svc_name, svc)
            return svc

        svc = mgr.get(self.service_name)
        if not isinstance(svc, RestServiceMixin):
            raise RuntimeError("Service '{}' does not implement RestService mixin".format(self.service_name))
        return svc
