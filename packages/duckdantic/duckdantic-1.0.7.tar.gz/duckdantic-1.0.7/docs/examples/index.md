# Examples

Real-world examples demonstrating Duckdantic usage patterns.

## Example Categories

### Pydantic Integration _(Coming Soon)_

Working with Pydantic models, validation, and conversion.

### Dataclasses _(Coming Soon)_

Using Duckdantic with Python dataclasses.

### TypedDict _(Coming Soon)_

Structural typing with TypedDict classes.

### Duck Typing Patterns _(Coming Soon)_

Advanced duck typing patterns and techniques.

## Quick Examples

### API Response Validation

```python
from duckdantic import TraitSpec, FieldSpec, satisfies

# Define expected API response structure
APIResponseTrait = TraitSpec(
    name="APIResponse",
    fields=(
        FieldSpec("status", str, required=True),
        FieldSpec("data", dict, required=True),
        FieldSpec("timestamp", float, required=True),
        FieldSpec("error", str, required=False),
    )
)

def handle_api_response(response: dict):
    if not satisfies(response, APIResponseTrait):
        raise ValueError("Invalid API response format")

    if response["status"] == "error":
        raise Exception(response.get("error", "Unknown error"))

    return response["data"]

# Usage
response = {
    "status": "success",
    "data": {"user_id": 123, "name": "Alice"},
    "timestamp": 1234567890.0
}

data = handle_api_response(response)
print(data)  # {'user_id': 123, 'name': 'Alice'}
```

### Configuration Management

```python
from duckdantic import Duck, DuckModel
from pydantic import BaseModel
from typing import Optional

class DatabaseConfig(BaseModel):
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_enabled: bool = False
    connection_timeout: int = 30

class CacheConfig(BaseModel):
    host: str
    port: int
    ttl: int = 3600

class AppConfig(DuckModel):
    database: DatabaseConfig
    cache: CacheConfig
    debug: bool = False

# Create duck types
DatabaseDuck = Duck(DatabaseConfig)
AppConfigDuck = Duck(AppConfig)

def load_config(config_dict: dict) -> AppConfig:
    """Load and validate application configuration."""
    # Validate structure
    if not isinstance(config_dict, AppConfigDuck):
        raise ValueError("Invalid configuration structure")

    # Convert to model
    config = AppConfig.from_duck(config_dict)

    # Additional validation
    if config.database.port < 1 or config.database.port > 65535:
        raise ValueError("Invalid database port")

    return config

# Usage
config_data = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "database": "myapp",
        "username": "user",
        "password": "secret"
    },
    "cache": {
        "host": "localhost",
        "port": 6379
    },
    "debug": True
}

config = load_config(config_data)
print(f"Connecting to {config.database.host}:{config.database.port}")
```

### Plugin System

```python
from duckdantic import TraitSpec, FieldSpec, MethodSpec, satisfies, methods_satisfy
from typing import Protocol, runtime_checkable

# Define plugin interface
PluginTrait = TraitSpec(
    name="Plugin",
    fields=(
        FieldSpec("name", str, required=True),
        FieldSpec("version", str, required=True),
        FieldSpec("description", str, required=False),
    )
)

PluginMethods = [
    MethodSpec("initialize", params=[], returns=bool),
    MethodSpec("execute", params=[dict], returns=dict),
    MethodSpec("cleanup", params=[], returns=None),
]

@runtime_checkable
class PluginProtocol(Protocol):
    name: str
    version: str

    def initialize(self) -> bool: ...
    def execute(self, data: dict) -> dict: ...
    def cleanup(self) -> None: ...

class PluginRegistry:
    def __init__(self):
        self.plugins = {}

    def register(self, plugin_class: type) -> None:
        """Register a plugin class."""
        # Check structural requirements
        if not satisfies(plugin_class, PluginTrait):
            raise TypeError("Plugin missing required attributes")

        if not methods_satisfy(plugin_class, PluginMethods):
            raise TypeError("Plugin missing required methods")

        # Create instance
        plugin = plugin_class()

        # Verify it's a valid plugin
        if not isinstance(plugin, PluginProtocol):
            raise TypeError("Plugin doesn't implement protocol")

        self.plugins[plugin.name] = plugin
        print(f"Registered plugin: {plugin.name} v{plugin.version}")

# Example plugin
class DataTransformPlugin:
    name = "data_transform"
    version = "1.0.0"
    description = "Transform data between formats"

    def initialize(self) -> bool:
        print("Initializing data transform plugin")
        return True

    def execute(self, data: dict) -> dict:
        # Transform data somehow
        return {k: str(v).upper() for k, v in data.items()}

    def cleanup(self) -> None:
        print("Cleaning up data transform plugin")

# Usage
registry = PluginRegistry()
registry.register(DataTransformPlugin)

plugin = registry.plugins["data_transform"]
result = plugin.execute({"name": "alice", "role": "admin"})
print(result)  # {'name': 'ALICE', 'role': 'ADMIN'}
```

### Form Validation with Type Coercion

```python
from duckdantic import Duck, as_duck
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

class RegistrationForm(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(ge=13, le=120)
    birth_date: date
    terms_accepted: bool
    referral_code: Optional[str] = None

    @field_validator('username')
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

# Create duck type for form validation
FormDuck = Duck(RegistrationForm)

def process_registration(form_data: dict):
    """Process user registration with validation."""
    # Quick structural check
    if not isinstance(form_data, FormDuck):
        missing_fields = []
        for field in RegistrationForm.model_fields:
            if field not in form_data:
                missing_fields.append(field)
        raise ValueError(f"Missing required fields: {missing_fields}")

    try:
        # Convert and validate
        form = as_duck(RegistrationForm, form_data)
    except Exception as e:
        raise ValueError(f"Validation error: {e}")

    # Check business rules
    if not form.terms_accepted:
        raise ValueError("Terms must be accepted")

    # Process registration
    print(f"Registering user: {form.username} ({form.email})")
    return form

# Usage
form_data = {
    "username": "alice_123",
    "email": "alice@example.com",
    "age": 25,
    "birth_date": "1998-01-01",
    "terms_accepted": True
}

user = process_registration(form_data)
```

### Data Migration

```python
from duckdantic import TraitSpec, FieldSpec, satisfies, Duck
from pydantic import BaseModel
from typing import List, Optional

# Old schema
OldUserTrait = TraitSpec(
    name="OldUser",
    fields=(
        FieldSpec("user_id", int, required=True),
        FieldSpec("full_name", str, required=True),
        FieldSpec("email_address", str, required=True),
    )
)

# New schema
class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    created_at: Optional[str] = None

UserDuck = Duck(User)

def migrate_user(old_data: dict) -> User:
    """Migrate user from old schema to new."""
    # Verify old format
    if not satisfies(old_data, OldUserTrait):
        raise ValueError("Invalid old user format")

    # Transform data
    name_parts = old_data["full_name"].split(" ", 1)
    new_data = {
        "id": old_data["user_id"],
        "first_name": name_parts[0],
        "last_name": name_parts[1] if len(name_parts) > 1 else "",
        "email": old_data["email_address"],
    }

    # Validate new format
    if not isinstance(new_data, UserDuck):
        raise ValueError("Migration produced invalid user")

    return UserDuck.convert(new_data)

# Batch migration
def migrate_users(old_users: List[dict]) -> List[User]:
    """Migrate a batch of users."""
    migrated = []
    errors = []

    for i, old_user in enumerate(old_users):
        try:
            new_user = migrate_user(old_user)
            migrated.append(new_user)
        except Exception as e:
            errors.append((i, str(e)))

    if errors:
        print(f"Migration completed with {len(errors)} errors")
        for idx, error in errors:
            print(f"  User {idx}: {error}")

    return migrated

# Usage
old_users = [
    {"user_id": 1, "full_name": "Alice Smith", "email_address": "alice@example.com"},
    {"user_id": 2, "full_name": "Bob", "email_address": "bob@example.com"},
    {"user_id": 3, "full_name": "Charlie David Jones", "email_address": "charlie@example.com"},
]

new_users = migrate_users(old_users)
for user in new_users:
    print(f"User {user.id}: {user.first_name} {user.last_name} ({user.email})")
```

## Best Practices

1. **Define Traits Once**: Create traits at module level and reuse them
2. **Use Duck API**: For Pydantic models, prefer the Duck API
3. **Validate Early**: Check structure before processing
4. **Provide Context**: Use explain() to give users helpful error messages
5. **Cache Duck Types**: Create duck types once for better performance
