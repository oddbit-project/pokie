from rick.mixin import Injectable


class SampleService(Injectable):

    def hello(self, name: str = "world") -> str:
        return "Hello, {}!".format(name)
