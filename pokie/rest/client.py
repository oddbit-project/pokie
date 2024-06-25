import json
import requests
from requests import Response


class RestResponse:
    def __init__(self, response:Response):
        self.success = True
        self.error = None
        self.data = None
        self.error_message = ""
        self.form_error = {}
        self.code = 0

        if response is None:
            return

        self.code = response.status_code
        self.success = response.status_code == 200

        data = response.json()
        if data:
            if "data" in data.keys():
                self.data = data["data"]

            if "error" in data.keys():
                self.error = data["error"]
                if "message" in self.error.keys():
                    self.error_message = self.error["message"]
                if "formError" in self.error.keys():
                    self.form_error = self.error["formError"]


class RestAuthInterface:

    def authenticate(self, client) -> bool:
        pass

class RestClient:
    def __init__(self, base_url="",auth:RestAuthInterface=None, headers:dict = None):
        self.session = requests.Session()
        self.base_url = base_url
        if not headers:
            headers = {"Content-type": "application/json"}
        self.headers = headers
        self.authenticated = auth is None
        if not self.authenticated:
            if not auth.authenticate(self):
                raise RuntimeError("REST authentication failed")
            self.authenticated = True

    def post(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.session.post(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )

    def post_formdata(self, url: str, data=None, files=None) -> RestResponse:
        return RestResponse(
            self.session.post("{}{}".format(self.base_url, url), data=data, files=files)
        )

    def get(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.session.get(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )

    def put(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.session.put(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )

    def delete(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.session.delete(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )
