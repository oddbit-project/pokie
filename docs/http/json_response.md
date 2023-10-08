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

# CamelCaseJsonResponse class

The *CamelCaseJsonResponse* modifies *JsonResponse* behaviour by attempting to camelCase JSON fields on the response.
This provides an effective mechanism to generate camelCase structures from snake_case sources, such as FieldMapper objects
or other commonly used Python structures.

Example:
```python
    
    # our response data
    data = {
        "first_name": "John",
        "last_name": "Connor",
    }
    
    # build response object
    response = CamelCaseJsonResponse(data)
    
    # output: '{"success":true,"data":{"firstName":"John", "lastName":"Connor"}'
    print(response.get_data(True))

```