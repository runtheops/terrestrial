from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def add_url_converter(self, name, converter):

    def register_converter(state):
            state.app.url_map.converters[name] = converter

    self.record_once(register_converter)
