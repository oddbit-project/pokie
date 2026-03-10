from rick.event import EventHandler


class ExampleEventHandler(EventHandler):

    def my_event_name(self, _in=None, out=None):
        """
        Sample event handler
        :param _in: entry object
        :param out: return object
        :return:
        """

        # example: append result to mutable output list
        if out is not None:
            out.append({"handler": "ExampleEventHandler", "status": "ok"})
