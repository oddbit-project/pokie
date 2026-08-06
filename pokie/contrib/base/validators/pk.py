import logging

from flask import current_app, has_app_context
from rick.base import Di
from rick.mixin import Translator
from rick.validator import registry
from rick.validator import Rule

from pokie.constants import DI_SERVICES
from pokie.contrib.base.constants import SVC_VALIDATOR

logger = logging.getLogger(__name__)

# fallback dependency injector for non-request contexts (eg. CLI)
_di = None


def init_validators(di: Di):
    global _di
    _di = di


def _resolve_di():
    # prefer the active application's Di so concurrent requests across multiple
    # FlaskApplication instances never clobber each other via the module global
    if has_app_context():
        di = getattr(current_app, "di", None)
        if di is not None:
            return di
    return _di


@registry.register_cls(name="pk")
class DbPrimaryKey(Rule):
    MSG_ERROR = "Invalid primary key value"

    def validate(
        self, value, options: list = None, error_msg=None, translator: Translator = None
    ):
        if len(options) == 0:
            raise RuntimeError("DbPrimaryKey(): missing table name")

        di = _resolve_di()
        if di is None:
            raise RuntimeError("DbPrimaryKey(): di not initialized")

        table_name = str(options[0])
        tokens = table_name.split(".")
        if len(tokens) > 2 or len(tokens) == 0:
            raise ValueError(
                "DbPrimaryKey(): invalid table name '{}'".format(table_name)
            )
        schema = None

        if len(tokens) == 2:
            table_name = tokens[1]
            schema = tokens[0]
        else:
            table_name = tokens[0]

        pk_name = ""
        if len(options) > 1:
            pk_name = str(options[1])

        svc = di.get(DI_SERVICES).get(SVC_VALIDATOR)
        try:
            if svc.id_exists(pk_name, value, table_name, schema):
                return True, ""
            return False, self.error_message(error_msg, translator)

        except Exception as e:
            logger.exception("DbPrimaryKey validation error for table '%s': %s", table_name, e)
            return False, self.error_message(error_msg, translator)
