import json
import logging

from flask.views import MethodView
from flask import current_app, jsonify
from flask_login import current_user
from rick.serializer.json import ExtendedJsonEncoder
from rick.form import RequestRecord

from .response import JsonRequestError, JsonStatus
from pokie.constants import HTTP_OK, HTTP_BADREQ, HTTP_INTERNAL_ERROR, HTTP_NOAUTH, HTTP_FORBIDDEN, DI_SERVICE_MANAGER


class PokieView(MethodView):

    def __init__(self):
        super().__init__()
        self.di = current_app.di

    def json(self, data, code=HTTP_OK):
        """
        Adaptation of flask's jsonify using Rick's ExtendedJsonEncoder
        :param data:
        :param code:
        :return:
        """
        indent = None
        separators = (",", ":")

        if current_app.config["JSONIFY_PRETTYPRINT_REGULAR"] or current_app.debug:
            indent = 2
            separators = (", ", ": ")

        data = json.dumps(data, indent=indent, separators=separators, cls=ExtendedJsonEncoder)
        return current_app.response_class(data, status=code, mimetype=current_app.config["JSONIFY_MIMETYPE"])

    def error(self, message=None, code=HTTP_BADREQ):
        data = JsonStatus(success=False, message=message if message else "operation failed")
        return self.json(data, code)

    def request_error(self, req: RequestRecord, code=HTTP_BADREQ):
        return self.json(JsonRequestError(success=False, formError=req.get_errors()), code)

    def success_message(self, message=''):
        return self.json(JsonStatus(success=True, message=message))

    def success(self, data=None, code=HTTP_OK):
        if data is None:
            return self.json(JsonStatus(success=True, message=''), code=code)
        return self.json(data, code)

    def empty_body(self):
        return self.error('empty body', code=HTTP_BADREQ)

    def not_found(self):
        return self.error("record not found", code=HTTP_BADREQ)

    def forbidden(self):
        return self.error("access denied", code=HTTP_FORBIDDEN)

    def denied(self):
        return self.error("access denied", code=HTTP_NOAUTH)

    def get_service(self, service_name):
        return self.di.get(DI_SERVICE_MANAGER).get(service_name)


class PokieAuthView(PokieView):
    # list of acls to check for current user
    # if list is empty, no acl control is used
    acl = []
    user = None

    def __init__(self):
        super().__init__()
        self.user = current_user

    def dispatch_request(self, *args, **kwargs):

        if not current_user.is_authenticated:
            return self.denied()

        for acl in self.acl:
            if not self.user.can_access(acl):
                return self.forbidden()

        try:
            return super().dispatch_request(*args, **kwargs)

        except Exception as e:
            logging.exception(e)
            return self.error("there was an internal error processing the request", code=HTTP_INTERNAL_ERROR)
