class RestServiceMixin:

    def get(self, id_record):
        pass

    def delete(self, id_record):
        pass

    def insert(self, record):
        pass

    def update(self, id_record, record):
        pass

    def exists(self, id_record):
        pass

    def list(self, search_text: str = None, match_fields: dict = None, limit: int = None, offset: int = None, sort_fields: dict = None):
        return 0, []