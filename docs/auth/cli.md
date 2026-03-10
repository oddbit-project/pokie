# Auth CLI Commands

The auth module provides CLI commands for managing users, roles, and resources. These commands are available when the
`pokie.contrib.auth` module is loaded.

## User Commands

### user:create

Create a new user.

```shell
$ python main.py user:create <username> <email> [options]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `username` | Yes | Username (1-200 characters) |
| `email` | Yes | Email address (3-200 characters) |
| `-f`, `--first_name` | No | First name (max 100 characters) |
| `-l`, `--last_name` | No | Last name (max 100 characters) |
| `-p`, `--password` | No | Prompt for password |
| `--enabled` | No | Enable user (default: True) |
| `--admin` | No | Create as admin (default: False) |

### user:info

Display user details.

```shell
$ python main.py user:info <username>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `username` | Yes | Username to look up |

Displays: id, username, active, admin, first_name, last_name, email, creation_date, last_login, attributes.

### user:mod

Modify user details.

```shell
$ python main.py user:mod <username> [options]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `username` | Yes | Username to modify |
| `-p`, `--password` | No | Change password (prompts for input) |
| `-a`, `--noadmin` | No | Remove admin privileges |
| `-A`, `--admin` | No | Grant admin privileges |
| `-d`, `--disabled` | No | Disable user |
| `-e`, `--enabled` | No | Enable user |

At least one modification option is required. Conflicting options (e.g. `--admin` and `--noadmin`) cannot be used
together.

### user:list

List all users.

```shell
$ python main.py user:list [options]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `-o`, `--offset` | No | Start offset (default: 0) |
| `-c`, `--count` | No | Number of records (default: 100) |
| `-i`, `--id` | No | Sort by ID instead of username |

### user:role

List roles assigned to a user.

```shell
$ python main.py user:role <username>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `username` | Yes | Username to look up |

## Role Commands

### role:list

List all ACL roles.

```shell
$ python main.py role:list
```

### role:create

Create a new ACL role.

```shell
$ python main.py role:create <description>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `description` | Yes | Role description (1-200 characters) |

### role:remove

Remove an ACL role.

```shell
$ python main.py role:remove <id_role> [options]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `id_role` | Yes | Role ID to remove |
| `-f`, `--force` | No | Force removal (removes all associations first) |

Without `--force`, the command fails if the role has associated users or resources.

### role:info

List resources associated with a role.

```shell
$ python main.py role:info <id_role>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `id_role` | Yes | Role ID |

### role:link

Assign a user to a role.

```shell
$ python main.py role:link <username> <id_role>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `username` | Yes | Username |
| `id_role` | Yes | Role ID |

### role:unlink

Remove a user from a role.

```shell
$ python main.py role:unlink <username> <id_role>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `username` | Yes | Username |
| `id_role` | Yes | Role ID |

## Resource Commands

### resource:list

List all ACL resources.

```shell
$ python main.py resource:list
```

### resource:create

Create a new ACL resource.

```shell
$ python main.py resource:create <id> <description>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `id` | Yes | Resource identifier (1-200 characters) |
| `description` | Yes | Resource description (1-200 characters) |

### resource:link

Associate a resource with a role.

```shell
$ python main.py resource:link <id_role> <id_resource>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `id_role` | Yes | Role ID |
| `id_resource` | Yes | Resource identifier |

### resource:unlink

Remove a resource association from a role.

```shell
$ python main.py resource:unlink <id_role> <id_resource>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `id_role` | Yes | Role ID |
| `id_resource` | Yes | Resource identifier |
