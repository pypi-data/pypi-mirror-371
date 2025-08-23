# Traits In Depth

This guide covers advanced trait features and patterns.

## Understanding Traits

A trait is a structural specification that defines:

- Required and optional fields
- Field types and constraints
- Metadata for organization

### Trait Anatomy

```python
from duckdantic import TraitSpec, FieldSpec

trait = TraitSpec(
    name="Example",              # Human-readable name
    fields=(                     # Tuple of field specifications
        FieldSpec(...),
        FieldSpec(...),
    ),
    metadata={"version": "1.0"}  # Optional metadata
)
```

## Field Specifications

### Complete FieldSpec Options

```python
from duckdantic import FieldSpec

field = FieldSpec(
    name="email",              # Field name to match
    typ=str,                   # Expected type
    required=True,             # Must be present?
    accept_alias=True,         # Check aliases?
    check_types=True,          # Enforce type checking?
    custom_matcher=None        # Custom validation function
)
```

### Custom Matchers

Define custom type validation logic:

```python
def email_matcher(actual_type, desired_type):
    """Custom matcher for email validation."""
    # Check if it's a string
    if actual_type != str:
        return False
    # Could add more validation here
    return True

EmailField = FieldSpec(
    name="email",
    typ=str,
    custom_matcher=email_matcher
)

# Use in trait
UserTrait = TraitSpec(
    name="User",
    fields=(EmailField,)
)
```

### Complex Types

Work with generic and union types:

```python
from typing import List, Dict, Union, Optional, Literal

ComplexTrait = TraitSpec(
    name="Complex",
    fields=(
        # Lists and dictionaries
        FieldSpec("tags", List[str]),
        FieldSpec("scores", Dict[str, float]),

        # Unions
        FieldSpec("id", Union[int, str]),

        # Optional (None or type)
        FieldSpec("nickname", Optional[str]),

        # Literals
        FieldSpec("status", Literal["active", "inactive"]),
    )
)
```

## Trait Composition

### Union - Either/Or

Accept objects that satisfy either trait:

```python
from duckdantic import union

CustomerTrait = TraitSpec(
    name="Customer",
    fields=(
        FieldSpec("customer_id", int),
        FieldSpec("company", str),
    )
)

EmployeeTrait = TraitSpec(
    name="Employee",
    fields=(
        FieldSpec("employee_id", int),
        FieldSpec("department", str),
    )
)

# Accept either customers or employees
PersonTrait = union(CustomerTrait, EmployeeTrait)

# These both satisfy PersonTrait
customer = {"customer_id": 1, "company": "ACME"}
employee = {"employee_id": 2, "department": "IT"}
```

### Intersection - Both/And

Require fields from both traits:

```python
from duckdantic import intersect

IdentifiableTrait = TraitSpec(
    name="Identifiable",
    fields=(FieldSpec("id", int),)
)

TimestampedTrait = TraitSpec(
    name="Timestamped",
    fields=(
        FieldSpec("created_at", str),
        FieldSpec("updated_at", str),
    )
)

# Requires id AND timestamps
RecordTrait = intersect(IdentifiableTrait, TimestampedTrait)

# Must have all fields
record = {
    "id": 1,
    "created_at": "2024-01-01",
    "updated_at": "2024-01-02"
}
```

### Minus - Subtraction

Remove fields from a trait:

```python
from duckdantic import minus

FullUserTrait = TraitSpec(
    name="FullUser",
    fields=(
        FieldSpec("id", int),
        FieldSpec("email", str),
        FieldSpec("password_hash", str),
        FieldSpec("api_key", str),
    )
)

# Remove sensitive fields
PublicUserTrait = minus(FullUserTrait, ["password_hash", "api_key"])

# Only needs id and email
public_data = {"id": 1, "email": "user@example.com"}
assert satisfies(public_data, PublicUserTrait)
```

## Field Aliases

### Working with Pydantic Aliases

```python
from pydantic import BaseModel, Field
from duckdantic import TraitSpec, FieldSpec, satisfies

class User(BaseModel):
    user_id: int = Field(alias="id")
    username: str = Field(alias="name")

# Trait can use either name
ByIdTrait = TraitSpec(
    name="HasId",
    fields=(FieldSpec("id", int),)  # Matches user_id via alias
)

user = User(id=1, name="alice")
assert satisfies(user, ByIdTrait)
```

### Validation vs Serialization Aliases

```python
from pydantic import AliasChoices

class APIModel(BaseModel):
    internal_id: int = Field(
        validation_alias=AliasChoices("id", "user_id"),
        serialization_alias="userId"
    )

# Can validate with different aliases
data1 = {"id": 1}
data2 = {"user_id": 1}
# Both work with validation aliases
```

## Trait Registry

Manage collections of traits:

```python
from duckdantic import TraitRegistry

registry = TraitRegistry()

# Register traits
registry.add(UserTrait)
registry.add(AdminTrait)
registry.add(GuestTrait)

# Find compatible traits
def find_role(obj):
    compatible = registry.find_compatible(obj, POLICY_PRAGMATIC)
    roles = [name for name, satisfied in compatible.items() if satisfied]
    return roles

user_data = {"id": 1, "email": "admin@example.com", "is_admin": True}
roles = find_role(user_data)  # ['User', 'Admin']
```

## Advanced Patterns

### Versioned Traits

Use metadata for versioning:

```python
UserV1 = TraitSpec(
    name="User",
    fields=(
        FieldSpec("id", int),
        FieldSpec("name", str),
    ),
    metadata={"version": "1.0"}
)

UserV2 = TraitSpec(
    name="User",
    fields=(
        FieldSpec("id", int),
        FieldSpec("name", str),
        FieldSpec("email", str),  # New in v2
    ),
    metadata={"version": "2.0"}
)

def get_user_version(data):
    if satisfies(data, UserV2):
        return "2.0"
    elif satisfies(data, UserV1):
        return "1.0"
    return None
```

### Nested Traits

Check nested structures:

```python
AddressTrait = TraitSpec(
    name="Address",
    fields=(
        FieldSpec("street", str),
        FieldSpec("city", str),
        FieldSpec("postal_code", str),
    )
)

# For nested checking, validate the nested object
def has_valid_address(obj):
    if not hasattr(obj, "address"):
        return False
    return satisfies(obj.address, AddressTrait)
```

### Trait Factories

Create traits programmatically:

```python
def create_crud_trait(entity_name: str, id_type=int):
    """Create standard CRUD traits for an entity."""
    base_fields = (
        FieldSpec("id", id_type, required=True),
        FieldSpec("created_at", str, required=True),
        FieldSpec("updated_at", str, required=True),
    )

    return {
        "create": TraitSpec(
            name=f"{entity_name}Create",
            fields=base_fields[1:]  # No ID on create
        ),
        "read": TraitSpec(
            name=f"{entity_name}Read",
            fields=base_fields
        ),
        "update": TraitSpec(
            name=f"{entity_name}Update",
            fields=(base_fields[0], base_fields[2])  # ID and updated_at
        )
    }

# Generate traits for different entities
user_traits = create_crud_trait("User")
post_traits = create_crud_trait("Post", id_type=str)
```

### Conditional Fields

Implement conditional requirements:

```python
def create_order_trait(premium_user: bool):
    base_fields = [
        FieldSpec("order_id", int, required=True),
        FieldSpec("items", list, required=True),
        FieldSpec("total", float, required=True),
    ]

    if premium_user:
        base_fields.extend([
            FieldSpec("discount_code", str, required=False),
            FieldSpec("priority_shipping", bool, required=False),
        ])

    return TraitSpec(
        name="Order",
        fields=tuple(base_fields)
    )

# Different traits for different user types
regular_order_trait = create_order_trait(premium_user=False)
premium_order_trait = create_order_trait(premium_user=True)
```

## Performance Considerations

### Trait Reuse

```python
# Good - create once
USER_TRAIT = TraitSpec(...)

def validate_users(users):
    return [u for u in users if satisfies(u, USER_TRAIT)]

# Bad - recreate each time
def validate_users_bad(users):
    trait = TraitSpec(...)  # Don't do this
    return [u for u in users if satisfies(u, trait)]
```

### Caching Benefits

The normalization cache helps with repeated checks:

```python
# These benefit from caching
users = [{"id": i, "name": f"User{i}"} for i in range(1000)]
results = [satisfies(u, UserTrait) for u in users]
# Second run is much faster due to cache
```

## Best Practices

1. **Name traits clearly**: Use descriptive names that indicate purpose
2. **Keep traits focused**: Each trait should represent one concept
3. **Use composition**: Build complex traits from simple ones
4. **Document requirements**: Add docstrings to complex traits
5. **Version carefully**: Use metadata for versioning when needed

## Next Steps

- Learn about [Type Policies](policies.md) for customization
- Explore Advanced Topics (coming soon) for optimization
- Check out [Examples](../examples/index.md) for real-world usage
