import json


class RestResponse:
    def __init__(self, response):
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

        if response.data:
            data = json.loads(response.data)

            if "data" in data.keys():
                self.data = data["data"]

            if "error" in data.keys():
                self.error = data["error"]
                if "message" in self.error.keys():
                    self.error_message = self.error["message"]
                if "formError" in self.error.keys():
                    self.form_error = self.error["formError"]


class RestClient:
    def __init__(self, client, base_url="/v1"):
        self.client = client
        self.base_url = base_url
        self.headers = {"Content-type": "application/json"}

    def post(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.client.post(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )

    def post_formdata(self, url: str, data=None, files=None) -> RestResponse:
        return RestResponse(
            self.client.post("{}{}".format(self.base_url, url), data=data, files=files)
        )

    def get(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.client.get(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )

    def put(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.client.put(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )

    def delete(self, url: str, data=None) -> RestResponse:
        return RestResponse(
            self.client.delete(
                "{}{}".format(self.base_url, url), json=data, headers=self.headers
            )
        )
