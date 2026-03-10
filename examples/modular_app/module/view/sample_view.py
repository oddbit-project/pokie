from flask import request

from pokie.http import PokieView
from module.constants import SVC_SAMPLE


class SampleView(PokieView):
    """
    Example view demonstrating service usage within a module.

    Registered in Module.build() via:
        app.add_url_rule("/sample", methods=["GET"], view_func=SampleView.as_view("sample_index"))

    Usage:
        GET /sample              -> {"data": {"message": "Hello, world!"}}
        GET /sample?name=Pokie   -> {"data": {"message": "Hello, Pokie!"}}
    """

    def get(self):
        svc = self.get_service(SVC_SAMPLE)
        name = request.args.get("name", "world")
        message = svc.hello(name)
        return self.success({"message": message})
