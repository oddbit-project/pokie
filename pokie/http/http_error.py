from rick.base import Di
from rick.mixin import Injectable

from pokie.constants import HTTP_NOT_FOUND, HTTP_INTERNAL_ERROR, DI_FLASK
from .response import JsonResponse


class HttpErrorHandler(Injectable):
    ERROR_404 = "404 Not Found: The requested URL was not found on the server."
    ERROR_500 = "500 Internal Server Error"

    def __init__(self, di: Di):
        super().__init__(di)
        _app = di.get(DI_FLASK)

        def wrapper_404(e):
            return self.error_404(_app, e)

        def wrapper_500(e):
            return self.error_500(_app, e)

        # register global error handler
        _app.register_error_handler(404, wrapper_404)
        _app.register_error_handler(500, wrapper_500)

    def error_404(self, _app, e):
        r = self.response(
            error={"message": self.ERROR_404}, success=False, code=HTTP_NOT_FOUND
        )
        return r.assemble(_app)

    def error_500(self, _app, e):
        r = self.response(
            error={"message": self.ERROR_500}, success=False, code=HTTP_INTERNAL_ERROR
        )
        return r.assemble(_app)

    def response(self, **kwargs):
        return JsonResponse(**kwargs)
