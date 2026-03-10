# Access Control (ACL)

Pokie provides a role-based access control (RBAC) system. Users are assigned to roles, and roles are linked to
resources. A user can access a resource if any of their roles grants access to it.

## Data Model

The ACL system uses four database tables:

```
acl_role  ──┐
             ├── acl_role_resource (junction)
acl_resource┘

acl_role  ──┐
             ├── acl_user_role (junction)
user ───────┘
```

| Table | Description |
|-------|-------------|
| `acl_role` | Roles (e.g. "admin", "editor") |
| `acl_resource` | Named resources (e.g. "manage_users", "edit_posts") |
| `acl_role_resource` | Links roles to resources |
| `acl_user_role` | Links users to roles |

### DTO Records

**AclRoleRecord** (table: `acl_role`)

| Attribute | Column | Description |
|-----------|--------|-------------|
| `id` | `id_acl_role` | Primary key (auto-increment) |
| `description` | `description` | Role description |

**AclResourceRecord** (table: `acl_resource`)

| Attribute | Column | Description |
|-----------|--------|-------------|
| `id` | `id_acl_resource` | Primary key (string identifier) |
| `description` | `description` | Resource description |

**AclRoleResourceRecord** (table: `acl_role_resource`)

| Attribute | Column | Description |
|-----------|--------|-------------|
| `id` | `id_acl_role_resource` | Primary key |
| `id_role` | `fk_acl_role` | Foreign key to acl_role |
| `id_resource` | `fk_acl_resource` | Foreign key to acl_resource |

**AclUserRoleRecord** (table: `acl_user_role`)

| Attribute | Column | Description |
|-----------|--------|-------------|
| `id` | `id_acl_user_role` | Primary key |
| `id_role` | `fk_acl_role` | Foreign key to acl_role |
| `id_user` | `fk_user` | Foreign key to user |

## AclService

Access the service via the DI container:

```python
from pokie.contrib.auth.constants import SVC_ACL

svc_acl = di.get(DI_SERVICES).get(SVC_ACL)
```

### Role Operations

#### list_roles() -> List[AclRoleRecord]

Returns all roles ordered by ID.

#### get_role(id_role) -> Optional[AclRoleRecord]

Returns a single role by ID. Results are cached.

#### add_role(description) -> int

Creates a new role and returns its ID.

#### remove_role(id_role)

Deletes a role. May raise a database exception if the role has associated users or resources.

#### can_remove_role(id_role) -> bool

Returns `True` if the role has no associated users or resources.

#### truncate_role(id_role)

Removes a role and all its associations (resources and users). This is a cascading delete that:

1. Removes all resource associations (`truncate_role_resources`)
2. Removes all user associations (`truncate_role_users`)
3. Deletes the role itself (`remove_role`)

### Resource Operations

#### list_resources() -> List[AclResourceRecord]

Returns all resources ordered by ID.

#### get_resource(id_resource) -> Optional[AclResourceRecord]

Returns a single resource by ID.

#### add_resource(id_resource, description) -> str

Creates a new resource with the given string ID and description.

### Role-Resource Associations

#### add_role_resource(id_role, id_resource)

Links a resource to a role. Invalidates the role cache and per-user caches for all users assigned to the role.

#### remove_role_resource(id_role, id_resource)

Removes the link between a resource and a role.

#### list_role_resources(id_role) -> List[AclResourceRecord]

Returns all resources associated with a role. Results are cached.

### User-Role Associations

#### add_user_role(id_user, id_role)

Assigns a role to a user. Invalidates the user's role and resource caches.

#### remove_user_role(id_user, id_role)

Removes a role from a user.

#### list_role_user_id(id_role) -> List[int]

Returns the IDs of all users assigned to a role.

### User Access Resolution

#### get_user_roles(id_user) -> dict

Returns a dict of `{role_id: AclRoleRecord}` for all roles assigned to the user. Results are cached.

#### get_user_resources(id_user) -> dict

Returns a dict of `{resource_id: AclResourceRecord}` for all resources the user can access (resolved through
their roles). Results are cached.

## Using ACL with Views

The `PokieAuthView` class integrates with the ACL system via its `acl` class attribute. See
[Pokie Views](../http/views.md#pokieauthview) for details.

```python
from pokie.http import PokieAuthView


class AdminView(PokieAuthView):
    # require the "manage_users" resource
    acl = ["manage_users"]

    def get(self):
        return self.success({"message": "admin area"})
```

If the user does not have access to any of the listed resources, the view returns HTTP 403. If the user is not
authenticated, it returns HTTP 401.

## Caching

`AclService` uses the following cache keys (with a 1-day TTL):

| Key Pattern | Value |
|-------------|-------|
| `acl:role:{id}` | AclRoleRecord |
| `acl:role:{id}:resources` | List[AclResourceRecord] |
| `user:{id}:roles` | List of role IDs |
| `user:{id}:role_ids` | List of role IDs (for resource resolution) |

When role-resource associations change, the service invalidates not only the role cache but also the per-user caches
for all users assigned to that role, ensuring consistency.
