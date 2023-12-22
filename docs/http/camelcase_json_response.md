# CamelCaseJsonResponse class

The *CamelCaseJsonResponse* modifies [JsonResponse](json_response.md) behaviour by attempting to camelCase JSON fields on the response.
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