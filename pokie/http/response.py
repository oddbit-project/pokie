import json
import rick.serializer.json

from pokie.constants import HTTP_OK


class JsonResponse:
    """
    Default JSON response formatter

    The usual JSON response has the following format:

    success is True:
    {
        "success": True,
        "data": {...}
    }

    success is False:
    {
        "success": False,
        "error": {
            "message": "...",
            [...optional extra keys, such as formError...]
        }
    }
    """

    def __init__(
        self,
        data: dict = None,
        success: bool = True,
        error: dict = None,
        code: int = HTTP_OK,
        mime_type: str = "application/json",
        headers: list = None,
    ):
        """
        Constructor for standardized json response
        :param data:
        :param success:
        :param error:
        :param code:
        :param mime_type:
        :param headers:
        """
        self.mime_type = mime_type
        self.headers = headers
        self.code = code
        self.response = {"success": success}
        # success always has 'data' object
        if success and data is None:
            data = {}

        # error always has 'error' object
        if not success and error is None:
            error = {"message": "an error has occurred"}

        if data is not None:
            self.response["data"] = data
        if error is not None:
            self.response["error"] = error

    def assemble(self, _app, **kwargs):
        """
        Assemble Flask response object
        :param _app:
        :return: Response
        """
        indent = None
        separators = (",", ":")

        if _app.json.compact or _app.debug:
            indent = 2
            separators = (", ", ": ")

        data = json.dumps(
            self.response, indent=indent, separators=separators, cls=self.serializer()
        )
        # @todo: add self.headers to response
        return _app.response_class(data, status=self.code, mimetype=self.mime_type)

    def serializer(self) -> json.JSONEncoder:
        """
        Get JSON serializer
        :return:
        """
        return rick.serializer.json.ExtendedJsonEncoder
