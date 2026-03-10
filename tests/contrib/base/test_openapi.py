import io
import json
import os
import tempfile
from argparse import Namespace

from rick.resource.console import ConsoleWriter

from pokie.contrib.base.cli.openapi import OpenApiGenCmd
from pokie.contrib.base.cli.openapi_builder import (
    OpenApiBuilder,
    _flask_to_openapi_path,
    _parse_validators,
    _validator_to_schema,
)


class TestOpenApiBuilder:
    def test_empty_spec(self):
        builder = OpenApiBuilder(title="Test API", version="2.0.0")
        spec = builder.build()
        assert spec["openapi"] == "3.0.0"
        assert spec["info"]["title"] == "Test API"
        assert spec["info"]["version"] == "2.0.0"
        assert "paths" in spec
        assert "components" in spec

    def test_flask_to_openapi_path(self):
        assert _flask_to_openapi_path("/users/<int:id>") == "/users/{id}"
        assert _flask_to_openapi_path("/users/<string:name>") == "/users/{name}"
        assert _flask_to_openapi_path("/users/<id>") == "/users/{id}"
        assert _flask_to_openapi_path("/simple") == "/simple"

    def test_parse_validators_string(self):
        result = _parse_validators("required|numeric")
        assert "required" in result
        assert "numeric" in result

    def test_parse_validators_dict(self):
        result = _parse_validators({"required": None, "numeric": None})
        assert "required" in result
        assert "numeric" in result

    def test_parse_validators_empty(self):
        assert _parse_validators("") == []
        assert _parse_validators(None) == []

    def test_validator_to_schema_numeric(self):
        schema = _validator_to_schema(["numeric"])
        assert schema["type"] == "integer"

    def test_validator_to_schema_decimal(self):
        schema = _validator_to_schema(["decimal"])
        assert schema["type"] == "number"

    def test_validator_to_schema_bool(self):
        schema = _validator_to_schema(["bool"])
        assert schema["type"] == "boolean"

    def test_validator_to_schema_iso8601(self):
        schema = _validator_to_schema(["iso8601"])
        assert schema["type"] == "string"
        assert schema["format"] == "date-time"

    def test_validator_to_schema_maxlen(self):
        schema = _validator_to_schema(["maxlen:100"])
        assert schema["type"] == "string"
        assert schema["maxLength"] == 100

    def test_validator_to_schema_default(self):
        schema = _validator_to_schema(["unknown"])
        assert schema["type"] == "string"

    def test_json_response_schema(self):
        builder = OpenApiBuilder()
        spec = builder.build()
        assert "JsonResponse" in spec["components"]["schemas"]
        jr = spec["components"]["schemas"]["JsonResponse"]
        assert jr["type"] == "object"
        assert "success" in jr["properties"]


class TestOpenApiGenCmd:
    def test_generate_spec(self, pokie_app, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = OpenApiGenCmd(pokie_di, writer=writer)
        args = Namespace(
            file="", title="Test API", version="1.0.0", prefix=""
        )
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        spec = json.loads(output)
        assert spec["openapi"] == "3.0.0"
        assert len(spec["paths"]) > 0

    def test_generate_spec_with_prefix(self, pokie_app, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = OpenApiGenCmd(pokie_di, writer=writer)
        args = Namespace(
            file="", title="Test API", version="1.0.0", prefix="/customers"
        )
        result = cmd.run(args)
        assert result is True
        output = stdout.getvalue()
        spec = json.loads(output)
        # all paths should start with /customers
        for path in spec["paths"]:
            assert path.startswith("/customers")

    def test_generate_spec_to_file(self, pokie_app, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = OpenApiGenCmd(pokie_di, writer=writer)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name

        try:
            args = Namespace(
                file=tmp_path, title="Test API", version="1.0.0", prefix=""
            )
            result = cmd.run(args)
            assert result is True

            with open(tmp_path) as f:
                spec = json.load(f)
            assert spec["openapi"] == "3.0.0"
            assert len(spec["paths"]) > 0
        finally:
            os.unlink(tmp_path)

    def test_spec_has_customer_routes(self, pokie_app, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = OpenApiGenCmd(pokie_di, writer=writer)
        args = Namespace(
            file="", title="Test API", version="1.0.0", prefix=""
        )
        cmd.run(args)
        spec = json.loads(stdout.getvalue())

        # the test app registers /customers routes
        paths = list(spec["paths"].keys())
        customer_paths = [p for p in paths if "customers" in p]
        assert len(customer_paths) > 0

    def test_spec_methods(self, pokie_app, pokie_di):
        stdout = io.StringIO()
        writer = ConsoleWriter(stdout=stdout, stderr=io.StringIO())
        cmd = OpenApiGenCmd(pokie_di, writer=writer)
        args = Namespace(
            file="", title="Test API", version="1.0.0", prefix="/customers"
        )
        cmd.run(args)
        spec = json.loads(stdout.getvalue())

        # /customers should have get (list) method
        if "/customers" in spec["paths"]:
            assert "get" in spec["paths"]["/customers"]
