from flask.views import MethodView
from flask import current_app as app, jsonify
from flask_login import current_user


class BaseView(MethodView):
    user = None

    def __init__(self):
        self.di = app.di
        if current_user.is_authenticated:
            self.user = current_user
            logging.info("logged in as user {}, {}".format(str(self.user.id), self.user.record.username))
        else:
            logging.info("anonymous access")

    def error(self, message=None, http_code=400):
        response = {
            "success": False,
            "message": message if message else "operation failed"
        }
        return jsonify(response), http_code

    def request_error(self, data, http_code=400):
        return jsonify({"formError": data}), http_code

    def success(self, data=None, message=None, http_code=200):
        if data is None:
            data = {
                "success": True
            }
            if message:
                data['message'] = message

        return jsonify(data), http_code


class PokieView(MethodView):

    def __init__(self):
        self.di = app.di



class AuthView(PokieView):
    # list of acls to check for current user
    # if list is empty, no acl control is used
    acl = []
    user = None



