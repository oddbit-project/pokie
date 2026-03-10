from pokie.rest import RestView


class ReadOnlyView(RestView):
    allow_methods = ["get"]
