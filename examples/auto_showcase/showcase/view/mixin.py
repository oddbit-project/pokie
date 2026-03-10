from flask import current_app, request


class AuditMixin:
    dispatch_hooks = ["_hook_audit"]

    def _hook_audit(self, method, *args, **kwargs):
        current_app.logger.info("{} {}".format(request.method, request.path))
        return None
