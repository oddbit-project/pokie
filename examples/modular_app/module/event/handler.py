from rick.event import EventHandler


class ExampleEventHandler(EventHandler):

    def my_event_name(self, _in=None, out=None):
        """
        Sanple event handler
        :param _in: entry object
        :param out: return object
        :return:
        """

        # dummy operation
        out = []
