import re


# Standard JSON response schema used by PokieView
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "data": {},
        "error": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "formError": {"type": "object"},
            },
        },
    },
}

# Standard DbGrid query parameters
DBGRID_PARAMETERS = [
    {
        "name": "offset",
        "in": "query",
        "required": False,
        "schema": {"type": "integer", "default": 0},
        "description": "Number of records to skip",
    },
    {
        "name": "limit",
        "in": "query",
        "required": False,
        "schema": {"type": "integer", "default": 100},
        "description": "Maximum number of records to return",
    },
    {
        "name": "sort",
        "in": "query",
        "required": False,
        "schema": {"type": "string"},
        "description": "Sort expression (e.g. field:asc,field2:desc)",
    },
    {
        "name": "match",
        "in": "query",
        "required": False,
        "schema": {"type": "string"},
        "description": "Field match expression (e.g. field:value|field2:value)",
    },
    {
        "name": "search",
        "in": "query",
        "required": False,
        "schema": {"type": "string"},
        "description": "Search text",
    },
]

# Validator -> OpenAPI type mapping
VALIDATOR_TYPE_MAP = {
    "numeric": {"type": "integer"},
    "decimal": {"type": "number"},
    "bool": {"type": "boolean"},
    "iso8601": {"type": "string", "format": "date-time"},
}


def _flask_to_openapi_path(rule_path):
    """Convert Flask URL rule to OpenAPI path format.

    Flask: /customers/<string:id_record>
    OpenAPI: /customers/{id_record}
    """
    return re.sub(r"<(?:[^:>]+:)?([^>]+)>", r"{\1}", rule_path)


def _parse_validators(validator_str):
    """Parse a validator string into a list of validator names."""
    if not validator_str:
        return []
    if isinstance(validator_str, dict):
        return list(validator_str.keys())
    return [v.strip() for v in validator_str.split("|") if v.strip()]


def _validator_to_schema(validators):
    """Convert a list of validators to an OpenAPI schema."""
    schema = {"type": "string"}

    for v in validators:
        if v in VALIDATOR_TYPE_MAP:
            schema = dict(VALIDATOR_TYPE_MAP[v])
            break

        if v.startswith("maxlen:"):
            try:
                max_len = int(v.split(":")[1])
                schema["maxLength"] = max_len
            except (IndexError, ValueError):
                pass

    return schema


def _extract_path_parameters(rule):
    """Extract path parameters from a Flask URL rule."""
    params = []
    for arg in rule.arguments:
        param = {
            "name": arg,
            "in": "path",
            "required": True,
            "schema": {"type": "string"},
        }
        params.append(param)
    return params


class OpenApiBuilder:
    def __init__(self, title="Pokie API", version="1.0.0", description=""):
        self.spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
                "description": description,
            },
            "paths": {},
            "components": {"schemas": {}},
        }

    def add_route(self, rule, view_class=None):
        """Add a route to the spec from a Flask URL rule."""
        path = _flask_to_openapi_path(rule.rule)
        path_parameters = _extract_path_parameters(rule)

        # Skip static endpoint
        if rule.endpoint == "static":
            return

        # Methods to document (skip HEAD and OPTIONS)
        methods = [m.lower() for m in rule.methods if m not in ("HEAD", "OPTIONS")]
        if not methods:
            return

        if path not in self.spec["paths"]:
            self.spec["paths"][path] = {}

        for method in methods:
            operation = self._build_operation(rule, method, view_class, path_parameters)
            self.spec["paths"][path][method] = operation

    def _build_operation(self, rule, method, view_class, path_parameters):
        """Build an OpenAPI operation object for a given method."""
        # Build operation ID from endpoint
        operation_id = "{}_{}".format(rule.endpoint, method).replace(".", "_")

        # Build tags from the first path segment
        path = _flask_to_openapi_path(rule.rule)
        segments = [s for s in path.split("/") if s and not s.startswith("{")]
        tag = segments[0] if segments else "default"

        operation = {
            "operationId": operation_id,
            "tags": [tag],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/JsonResponse"}
                        }
                    },
                }
            },
        }

        # Add path parameters
        if path_parameters:
            operation["parameters"] = list(path_parameters)

        if view_class is not None:
            # Check if this is a list endpoint (GET without path params)
            is_list = method == "get" and not path_parameters
            has_record_class = getattr(view_class, "record_class", None) is not None

            # Add DbGrid query parameters for list endpoints
            if is_list and has_record_class:
                if "parameters" not in operation:
                    operation["parameters"] = []
                operation["parameters"].extend(DBGRID_PARAMETERS)

            # Add request body for write methods
            request_class = getattr(view_class, "request_class", None)
            if method in ("post", "put", "patch") and request_class is not None:
                schema = self._schema_from_request_class(request_class)
                schema_name = request_class.__name__
                self.spec["components"]["schemas"][schema_name] = schema
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/{}".format(schema_name)
                            }
                        }
                    },
                }
            elif method in ("post", "put", "patch") and has_record_class:
                # use record class for schema if no request class
                record_class = view_class.record_class
                schema = self._schema_from_record_class(record_class)
                schema_name = record_class.__name__
                if schema_name not in self.spec["components"]["schemas"]:
                    self.spec["components"]["schemas"][schema_name] = schema
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/{}".format(schema_name)
                            }
                        }
                    },
                }

        return operation

    def _schema_from_request_class(self, request_class):
        """Build an OpenAPI schema from a RequestRecord class."""
        schema = {"type": "object", "properties": {}, "required": []}

        # Instantiate to get fields
        try:
            instance = request_class()
            fields = instance.fields
        except Exception:
            # If instantiation fails (e.g. requires args), try class-level fields
            fields = getattr(request_class, "fields", {})

        if isinstance(fields, dict):
            for name, f in fields.items():
                # f can be a Field instance or a spec dict
                if isinstance(f, dict):
                    validators = f.get("validators", "")
                    required = f.get("required", False)
                else:
                    validators = getattr(f, "validators", "")
                    required = getattr(f, "required", False)

                validator_list = _parse_validators(validators)
                prop_schema = _validator_to_schema(validator_list)
                schema["properties"][name] = prop_schema

                if required or "required" in validator_list:
                    schema["required"].append(name)

        if not schema["required"]:
            del schema["required"]

        return schema

    def _schema_from_record_class(self, record_class):
        """Build an OpenAPI schema from a RickDb Record class."""
        schema = {"type": "object", "properties": {}}

        try:
            instance = record_class()
            # Get attribute names (non-private, non-callable)
            for name in dir(instance):
                if name.startswith("_"):
                    continue
                val = getattr(instance, name, None)
                if callable(val):
                    continue
                schema["properties"][name] = {"type": "string"}
        except Exception:
            pass

        return schema

    def build(self) -> dict:
        """Return the complete OpenAPI spec."""
        # Add the standard JsonResponse schema
        self.spec["components"]["schemas"]["JsonResponse"] = RESPONSE_SCHEMA
        return self.spec
