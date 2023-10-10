# JsonResponse class

The *JsonResponse* provides a standard JSON response for both success and error responses. The data is automatically
serialized using [Rick's ExtendedJsonEncoder](https://git.oddbit.org/OddBit/rick/src/branch/master/rick/serializer/json/json.py). As
such, uuid objects, datetime objects and FieldMapper records are supported.

Generated JSON Response format:

| Name    | Type               | Mandatory - success | Mandatory - error | Description                                     |
|---------|--------------------|---------------------|-------------------|-------------------------------------------------|
| success | bool               | yes                 | yes               | operation result status                         |
| data    | any                | yes                 | no                | returned data - may be empty on empty responses |
| error   | any (default dict) | no                  | yes               | returned error on failure                       |


Success response example:
```json
{
  "success": true,
  "data": (... JSON-encoded response ...)
}
```

Error response example (without a specific error payload):
```json
{
  "success": false,
  "error": {
    "message": "an error has occurred"
  }
}
```
