# User Management

The `UserService` provides user CRUD operations, authentication, password management, and token-based authentication.

## UserService

Access the service via the DI container:

```python
from pokie.contrib.auth.constants import SVC_USER

svc_user = di.get(DI_SERVICES).get(SVC_USER)
```

### Authentication

#### authenticate(username, password) -> Optional[UserRecord]

Validates credentials and returns a sanitized `UserRecord` (password field cleared) on success, or `None` on failure.

The method checks that the user exists, is active, and the password hash matches. If the existing hash uses a weak
algorithm, it is automatically upgraded to bcrypt. The `last_login` timestamp is updated on success.

```python
record = svc_user.authenticate("admin", "secret")
if record:
    print(f"Welcome, {record.username}")
```

### User Retrieval

#### load_id(id_user) -> Optional[UserRecord]

Returns a `UserRecord` with the password field cleared. Intended for safe transport/display.

#### get_by_id(id_user) -> Optional[UserRecord]

Returns the full `UserRecord` by primary key. Results are cached with a 1-day TTL.

#### get_by_username(username) -> Optional[UserRecord]

Returns the full `UserRecord` by username. Uses a two-level cache: username maps to user ID, then user ID maps to
the record.

#### list_users(offset, limit, sort_field=None, sort_order=None) -> tuple

Returns a tuple of `(total_count, [UserRecord, ...])`. Defaults to sorting by username.

```python
total, users = svc_user.list_users(0, 100)
```

### User Management

#### add_user(record) -> int

Creates a new user and returns the generated user ID.

```python
from pokie.contrib.auth.dto import UserRecord

record = UserRecord(
    username="newuser",
    email="user@example.com",
    password=svc_user.hasher.hash("password123"),
    active=True,
)
user_id = svc_user.add_user(record)
```

#### update_user(record)

Updates an existing user. Invalidates relevant caches, including the old username cache if the username changed.

#### update_password(id_user, password_hash) -> bool

Updates the password hash for a user and invalidates the user cache.

```python
new_hash = svc_user.hasher.hash("new_password")
svc_user.update_password(user_id, new_hash)
```

### Token-Based Authentication

Tokens provide an alternative authentication mechanism, useful for API keys or service-to-service authentication.

#### add_user_token(id_user, expires=None) -> UserTokenRecord

Creates a new random 128-character hex token for the specified user. Returns the `UserTokenRecord` with the
generated ID.

```python
from datetime import datetime, timezone, timedelta

# token with 30-day expiry
expires = datetime.now(timezone.utc) + timedelta(days=30)
token_record = svc_user.add_user_token(user_id, expires=expires)
print(token_record.token)  # 128-char hex string
```

#### get_user_by_token(token) -> Optional[UserRecord]

Validates the token (must be active and not expired) and returns the associated `UserRecord`, or `None`.

#### get_token(token) -> Optional[UserTokenRecord]

Returns the raw `UserTokenRecord` for a token string.

#### disable_user_token(id_user_token) -> bool

Marks a token as inactive and invalidates the token cache.

#### remove_user_token(id_user_token)

Permanently deletes a token record.

#### list_user_tokens(id_user) -> List[UserTokenRecord]

Returns all tokens for a given user.

#### prune_tokens()

Removes all expired tokens from the database.

## UserRecord

The `UserRecord` DTO maps to the `user` database table:

| Attribute | Column | Description |
|-----------|--------|-------------|
| `id` | `id_user` | Primary key |
| `active` | `active` | Account active flag |
| `admin` | `admin` | Admin flag |
| `username` | `username` | Unique username |
| `first_name` | `first_name` | First name |
| `last_name` | `last_name` | Last name |
| `email` | `email` | Email address |
| `creation_date` | `creation_date` | Account creation timestamp |
| `last_login` | `last_login` | Last login timestamp |
| `password` | `password` | Bcrypt password hash |
| `external` | `external` | External authentication flag |
| `attributes` | `attributes` | JSON attributes field |

## UserTokenRecord

The `UserTokenRecord` DTO maps to the `user_token` database table:

| Attribute | Column | Description |
|-----------|--------|-------------|
| `id` | `id_user_token` | Primary key |
| `creation_date` | `creation_date` | Token creation timestamp |
| `update_date` | `update_date` | Last update timestamp |
| `active` | `active` | Token active flag |
| `user` | `fk_user` | Foreign key to user |
| `token` | `token` | 128-char hex token string |
| `expires` | `expires` | Optional expiration timestamp |

## Password Hashing

Pokie uses bcrypt for password hashing via Rick's `BcryptHasher`. The `authenticate()` method includes automatic
weak hash detection and upgrade: if a password hash uses an older algorithm, it is transparently rehashed with bcrypt
on successful login.

## Caching

`UserService` uses the following cache keys (with a 1-day TTL):

| Key Pattern | Value |
|-------------|-------|
| `user:{id}` | UserRecord |
| `user:username:{username}` | User ID (int) |
| `user:token:{token}` | UserTokenRecord |

Caching is enabled when `AUTH_USE_CACHE` is `True` and `DI_CACHE` is available in the DI container. Otherwise, a
`DummyCache` is used as a no-op fallback.
