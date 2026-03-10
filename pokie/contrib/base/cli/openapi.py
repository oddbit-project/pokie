import json

from pokie.constants import DI_FLASK, DI_APP
from pokie.core import CliCommand
from .openapi_builder import OpenApiBuilder


class OpenApiGenCmd(CliCommand):
    description = "generate OpenAPI 3.0 specification"

    def arguments(self, parser):
        parser.add_argument("-f", dest="file", type=str, default="", help="output file")
        parser.add_argument(
            "--title", type=str, default="Pokie API", help="API title"
        )
        parser.add_argument(
            "--version", type=str, default="1.0.0", help="API version"
        )
        parser.add_argument(
            "--prefix", type=str, default="", help="filter routes by prefix"
        )

    def run(self, args) -> bool:
        pokie_app = self.get_di().get(DI_APP)
        pokie_app.init()
        app = self.get_di().get(DI_FLASK)

        builder = OpenApiBuilder(
            title=args.title,
            version=args.version,
        )

        with app.app_context():
            for rule in app.url_map.iter_rules():
                # filter by prefix if specified
                if args.prefix and not rule.rule.startswith(args.prefix):
                    continue

                # get view class if available
                view_func = app.view_functions.get(rule.endpoint)
                view_class = getattr(view_func, "view_class", None)
                builder.add_route(rule, view_class)

        spec = builder.build()
        output = json.dumps(spec, indent=2)

        if args.file:
            with open(args.file, "w") as f:
                f.write(output)
            self.tty.write("OpenAPI spec written to {}".format(args.file))
        else:
            self.tty.write(output)

        return True
