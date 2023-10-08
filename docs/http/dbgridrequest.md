# DbGridRequest class

The *DbGridRequest* class offers a convenient way of parsing and
validating [DbGrid](https://oddbit-project.github.io/rick_db/grid/) parameters from a REST endpoint.
It is the underlying mechanism used by [RestMixin](rest.md) listing functionality.

This class extracts and validates a set of parameters from a dictionary - usually from a GET request - against the list
of fields of the desired record type. Adittionally, it may also provide camelCase conversion functionality and sane
defaults on listing operations.

Please note that *DbGridRequest* does not perform actual field type validation - eg. performing exact matching on a
numeric
field with an arbitrary string will likely result in an exception.

## Supported parameters

| Name   | Type   | Example                          | Description                                                       |
|--------|--------|----------------------------------|-------------------------------------------------------------------|
| offset | int    | offset=1                         | optional OFFSET clause to apply to the SQL query                  |
| limit  | int    | limit=10                         | optional LIMIT clause to apply to the SQL query                   |
| sort   | string | sort="name:asc,age"              | optional list of field names and ordering for the ORDER by clause |
| match  | string | match="field:value\|field:value" | optional list of fields and values to perform exact matching      |
| search | string | search="john"                    | optional free text search string                                  |

### offset, limit

Numeric positive values to define the window for the results.

### sort

An optional list of field names to order by. Multiple field names can be separated by a comma. An optional ordering
direction can be specified by suffixing the field name with ":" and then the desired order (either *asc* or *desc*).
If no order is specified, a default ordering sequence is used.

### match

A list of fieldnames and values to perform exact match. The fieldnames and values are concatenated with ':', and
multiple
fieldname:value pairs can be concatenated with '|'.

Please note, no validation is perfomed on the value data type. Invalid data types used to perform exact matching may
result in exceptions when executing the SQL, so make sure any execution is wrapped with a try... Except handler.

### search

Free text search, to be performed on the specified specified search fields (defined when calling *dbgrid_parameters()*).
If no search fields are specified, this value will produce no effect.

## Class Methods

### **DBGridRequest(record: Type[Record], translator: Translator = None, use_camel_case=False)**

Instantiates a DBGridRequest using the FieldMapper *record*, with an optional translator object. If *use_camel_case* is
True,
camelCase field names are automatically converted to snake_case on both match and sorting operations - eg. the field "
phone_number"
can now also be referenced as "phoneNumber".

### **DBGridRequest.dbgrid_parameters(list_limit: int = 0, search_fields: list = None) -> dict**

This method returns a named dictionary with all the arguments required by *RestServiceMixin.list()*. It can optionally
receive a
default limit value to be applied to the query, and a list of field names to perform free text search.

## Usage

The typical usage scenario is as a regular RequestObject within a specific view method:

```python
from pokie.constants import DEFAULT_LIST_SIZE
from pokie.http import PokieView
from pokie.rest import DbGridRequest
from flask import request


class MyView(PokieView):

    def get(self):
        # MyDbRecord is the DTO record to be used
        req = DbGridRequest(MyDbRecord)

        # attempt to validate optional DbGrid GET parameters
        if not req.is_valid(request.args):
            return self.request_error(req)

        try:
            # self.svc is a RestServiceMixin object

            count, data = self.svc.list(
                **dbgrid_request.dbgrid_parameters(
                    DEFAULT_LIST_SIZE,  # apply default LIMIT clause
                    [MyDbRecord.name, ]  # limit free text search to the "name" field
                )
            )

            # assemble result
            result = {
                "total": count,
                "items": data
            }
            # return data
            return self.success(result)

        except Exception as e:
            # exception may happen because of mismatched data type, such as matching strings to int fields
            self.logger.exception(e)
            return self.error()
```