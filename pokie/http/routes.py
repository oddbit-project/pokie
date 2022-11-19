# predefined method names and route rule expansions
controller_action_map = {
    'list': ['/{slug}', ['GET'], '.list'],
    'show': ['/{slug}/<{type}:id>', ['GET'], '.show'],
    'create': ['/{slug}', ['POST'], '.create'],
    'update': ['/{slug}/<{type}:id>', ['PUT', 'PATCH'], '.update'],
    'delete': ['/{slug}/<{type}:id>', ['DELETE'], '.delete'],
}

# predefined resource methods and route rule expansions
resource_action_map = {
    # method_name: [rule, rule, ...]
    'get': [
        ['/{slug}', ['GET'], '.list'],
        ['/{slug}/<{type}:id>', ['GET'], '.show']
    ],
    'post': [
        ['/{slug}', ['POST'], '.create']
    ],
    'put': [
        ['/{slug}/<{type}:id>', ['PUT', 'PATCH'], '.update']
    ],
    'delete': [
        ['/{slug}/<{type}:id>', ['DELETE'], '.delete']
    ]
}


def route_controller(app, slug: str, cls, id_type:str='int'):
    """
    Register default routes for a controller class

    :param app: Flask app or blueprint
    :param slug: route base prefix
    :param cls: class to map
    :param id_type: optional datatype for id
    :return:
    """
    name = cls.__name__
    for method_name, opts in controller_action_map.items():
        route, methods, suffix = opts
        if callable(getattr(cls, method_name, None)):
            app.add_url_rule(route.format(slug=slug, type=id_type), methods=methods, view_func=cls.view_method(method_name))


def route_resource(app, slug, cls, id_type:str='int'):
    """
    Register default routes for a resource class

    :param app: Flask app or blueprint
    :param slug: route base prefix
    :param cls: class to map
    :param id_type: optional datatype for id
    :return:
    """
    name = ".".join([cls.__module__, cls.__name__])
    for view_name, routes in resource_action_map.items():
        for item in routes:
            route, methods, suffix = item
            if getattr(cls, view_name, None) is not None:
                app.add_url_rule(route.format(slug=slug, type=id_type), methods=methods,
                                 view_func=cls.as_view('{}{}'.format(name, suffix)))
