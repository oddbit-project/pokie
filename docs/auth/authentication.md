# Authentication

Pokie provides a session-based authentication module built on [Flask-Login](https://flask-login.readthedocs.io/). The
auth module handles user login/logout, session management, and integrates with the [ACL](acl.md) system for
access control.

## Enabling Authentication

Add the auth module to your module list in `main.py`:

```python
modules = [
    "pokie.contrib.auth",
    # your other modules...
]
```

The auth module requires `PgSqlFactory` in your factories list. If caching is desired, also include `RedisFactory` and
`CacheFactory` (see [Factories](../factories.md)).

## Configuration

| Attribute | Default | Description |
|-----------|---------|-------------|
| `AUTH_SECRET` | `""` | Secret key for Flask-Login session hashing |
| `AUTH_USE_CACHE` | `True` | Enable caching on User and ACL services |

> Note: If `AUTH_SECRET` is empty, a random key is generated at startup. This means sessions will not persist across
> application restarts. Always set `AUTH_SECRET` in production.

## Routes

The auth module registers the following routes:

| Method | Path | View | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | `LoginView` | Authenticate user |
| GET | `/auth/logout` | `LogoutView` | End user session |

### Login

**POST** `/auth/login`

**Request body:**

```json
{
    "username": "admin",
    "password": "secret",
    "remember": false
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `username` | Yes | Username |
| `password` | Yes | Password |
| `remember` | No | Persistent session (bool) |

**Success response:**

```json
{
    "success": true,
    "data": {
        "id_user": 1,
        "username": "admin",
        "active": true,
        "admin": false,
        "first_name": "",
        "last_name": "",
        "email": "admin@example.com",
        "password": "",
        "creation_date": "2024-01-01T00:00:00",
        "last_login": "2024-06-15T10:30:00",
        "external": false,
        "attributes": null
    }
}
```

> Note: The password field is always returned empty for security.

**Error response:**

```json
{
    "success": false,
    "error": {"message": "invalid credentials"}
}
```

### Logout

**GET** `/auth/logout`

Requires authentication. Clears the user session and returns a success response.

## Events

The login view dispatches an `afterLogin` event after successful authentication, before returning the response. This
can be used to perform actions such as logging or updating user activity. See [Events](../events.md) for details on
registering event handlers.

## Session Provider

The `SessionProvider` class initializes Flask-Login and manages session lifecycle. It is automatically created when the
auth module is built.

The provider registers a `user_loader` callback with Flask-Login that restores user sessions. On each request, it loads
the user record from `UserService` and rebuilds the `User` object with current roles and resources from `AclService`.

## User Class

The `User` class implements Flask-Login's user interface and provides role/resource checking:

```python
from pokie.contrib.auth import User

user = User(
    id_user=1,
    record=user_record,
    roles=[1, 2],         # list of role IDs
    resources=[10, 20],   # list of resource IDs
)

# Flask-Login properties
user.is_authenticated  # True if id_user is not None
user.is_anonymous      # True if id_user is None
user.is_active         # True if record.active is True

# ACL checks
user.can_access(10)    # True - resource 10 is in the list
user.has_role(1)       # True - role 1 is in the list

# Getters
user.get_id()          # "1" (string)
user.get_record()      # UserRecord instance
user.get_roles()       # [1, 2]
user.get_resources()   # [10, 20]
```

### UserInterface

`UserInterface` is an abstract base class defining the contract for user objects. Custom user implementations
must extend this class:

| Property / Method | Return Type | Description |
|------------------|-------------|-------------|
| `is_active` | bool | Whether the user account is active |
| `is_anonymous` | bool | Whether this is an anonymous user |
| `is_authenticated` | bool | Whether the user is authenticated |
| `get_id()` | str | String user ID for Flask-Login |
| `get_record()` | object | Underlying user record |
| `can_access(id_resource)` | bool | Check if user has access to resource |
| `has_role(id_role)` | bool | Check if user has a specific role |
| `get_roles()` | list | List of role IDs |
| `get_resources()` | list | List of resource IDs |

## Helper: build_user_acl

The `build_user_acl()` function constructs a `User` object with roles and resources loaded from `AclService`:

```python
from pokie.contrib.auth.provider.session_provider import build_user_acl

user = build_user_acl(di, user_record)
```

This is used internally by the session provider and login view, but can also be called directly when you need to
build a fully-populated `User` object from a `UserRecord`.
