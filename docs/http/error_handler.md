# Error Handling

## Flask errors

Pokie provides a pluggable class-based mechanism to override the default Flask error handlers and provide appropriate JSON responses
following the global JsonResponse format. These classes must extend *Injectable*. Please refer to the default class 
*pokie.http.HttpErrorHandler* for implementation details.

The error handler class to be used is defined by a configuration setting in *BaseConfigTemplate* - **CFG_HTTP_ERROR_HANLDER**.
The value of this setting is the canonical path name of the class to be used; By default, *pokie.http.HttpErrorHandler*.

The created object is also registered in the global registry, and can be accessed with the constant **DI_HTTP_ERROR_HANDLER**.

## **HttpErrorHandler class**

This class provides JSON-formatted responses for Flask errors for the following HTTP codes:

|Code|Message|
|---|---|
|400|400 Bad Request: The browser (or proxy) sent a request that this server could not understand.|
|404|404 Not Found: The requested URL was not found on the server.|
|405|405 Method Not Allowed: The method is not allowed for the requested URL.|
|500|500 Internal Server Error|

