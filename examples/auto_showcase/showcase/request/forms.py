from rick.form import RequestRecord, field


class ShipperRequest(RequestRecord):
    fields = {
        "id": field(validators="id"),
        "company_name": field(validators="required|maxlen:40"),
        "phone": field(validators="maxlen:24"),
    }
