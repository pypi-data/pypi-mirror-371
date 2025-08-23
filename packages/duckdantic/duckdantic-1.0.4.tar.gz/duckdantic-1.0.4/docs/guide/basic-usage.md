# Basic Usage

This guide covers the fundamental concepts and basic usage patterns of Duckdantic.

## Defining Traits

A trait is a specification of what fields an object should have:

```python
from duckdantic import TraitSpec, FieldSpec

# Define a simple trait
PersonTrait = TraitSpec(
    name="Person",
    fields=(
        FieldSpec("name", str, required=True),
        FieldSpec("age", int, required=True),
    )
)
```

### Field Specifications

Each field in a trait is defined by a `FieldSpec`:

```python
FieldSpec(
    name="email",          # Field name
    typ=str,              # Expected type
    required=True,        # Is it required?
    accept_alias=True,    # Accept field aliases?
    check_types=True,     # Enforce type checking?
)
```

### Optional Fields

Not all fields need to be required:

```python
ProfileTrait = TraitSpec(
    name="Profile",
    fields=(
        FieldSpec("username", str, required=True),   # Required
        FieldSpec("bio", str, required=False),       # Optional
        FieldSpec("website", str, required=False),   # Optional
    )
)
```

## Checking Satisfaction

Use `satisfies()` to check if an object matches a trait:

```python
from duckdantic import satisfies

# Check different object types
person_dict = {"name": "Alice", "age": 30}
assert satisfies(person_dict, PersonTrait)

class Employee:
    def __init__(self, name: str, age: int, dept: str):
        self.name = name
        self.age = age
        self.dept = dept

emp = Employee("Bob", 25, "Engineering")
assert satisfies(emp, PersonTrait)  # Extra fields are OK
```

## Getting Detailed Feedback

Use `explain()` to understand why validation fails:

```python
from duckdantic import explain

incomplete = {"name": "Charlie"}  # Missing age

result = explain(incomplete, PersonTrait)
print(result)
# {
#     'ok': False,
#     'missing': ['age'],
#     'type_conflicts': [],
#     'reasons': ["missing required field 'age'"]
# }
```

## Working with Types

### Basic Types

Duckdantic supports all Python types:

```python
ContactTrait = TraitSpec(
    name="Contact",
    fields=(
        FieldSpec("name", str),
        FieldSpec("age", int),
        FieldSpec("height", float),
        FieldSpec("active", bool),
        FieldSpec("tags", list),
        FieldSpec("metadata", dict),
    )
)
```

### Generic Types

Use typing module for more specific types:

```python
from typing import List, Dict, Optional

DetailedTrait = TraitSpec(
    name="Detailed",
    fields=(
        FieldSpec("tags", List[str]),
        FieldSpec("scores", Dict[str, float]),
        FieldSpec("nickname", Optional[str]),
    )
)
```

### Numeric Widening

By default, int satisfies float requirements:

```python
MeasurementTrait = TraitSpec(
    name="Measurement",
    fields=(FieldSpec("value", float, required=True),)
)

# Int satisfies float
int_measurement = {"value": 42}
assert satisfies(int_measurement, MeasurementTrait)
```

## Working with Different Object Types

### Dictionaries

The simplest case - dictionaries work directly:

```python
user_dict = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com"
}

assert satisfies(user_dict, UserTrait)
```

### Classes with Attributes

Any object with attributes works:

```python
class Customer:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

customer = Customer(2, "Bob")
assert satisfies(customer, UserTrait)
```

### Dataclasses

```python
from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    price: float

product = Product(1, "Widget", 9.99)
assert satisfies(product, ProductTrait)
```

### Pydantic Models

```python
from pydantic import BaseModel

class Order(BaseModel):
    id: int
    customer: str
    total: float

order = Order(id=1, customer="Alice", total=99.99)
assert satisfies(order, OrderTrait)
```

### TypedDict

```python
from typing import TypedDict

class PersonDict(TypedDict):
    name: str
    age: int

person: PersonDict = {"name": "Charlie", "age": 35}
assert satisfies(person, PersonTrait)
```

## Type Policies

Control how types are compared:

```python
from duckdantic import TypeCompatPolicy, satisfies

# Strict policy - no type coercion
strict_policy = TypeCompatPolicy(
    allow_numeric_widening=False,
    allow_optional_widening=False
)

# This would fail with strict policy
int_value = {"value": 42}
float_trait = TraitSpec(
    name="FloatValue",
    fields=(FieldSpec("value", float),)
)

assert satisfies(int_value, float_trait)  # True (default)
assert not satisfies(int_value, float_trait, strict_policy)  # False
```

## Trait Composition

Combine traits using set operations:

```python
from duckdantic import union, intersect, minus

# Base traits
UserTrait = TraitSpec(
    name="User",
    fields=(
        FieldSpec("id", int),
        FieldSpec("name", str),
    )
)

ContactTrait = TraitSpec(
    name="Contact",
    fields=(
        FieldSpec("email", str),
        FieldSpec("phone", str),
    )
)

# Union - accepts objects that satisfy either trait
FlexibleTrait = union(UserTrait, ContactTrait)

# Intersection - requires fields from both traits
CompleteUserTrait = intersect(UserTrait, ContactTrait)

# Minus - remove specific fields
PublicUserTrait = minus(UserTrait, ["internal_id"])
```

## Common Patterns

### API Response Validation

```python
SuccessResponseTrait = TraitSpec(
    name="SuccessResponse",
    fields=(
        FieldSpec("status", str),
        FieldSpec("data", dict),
        FieldSpec("timestamp", str),
    )
)

def handle_response(response: dict):
    if not satisfies(response, SuccessResponseTrait):
        raise ValueError("Invalid response format")

    # Safe to access fields
    return response["data"]
```

### Configuration Validation

```python
DatabaseConfigTrait = TraitSpec(
    name="DatabaseConfig",
    fields=(
        FieldSpec("host", str, required=True),
        FieldSpec("port", int, required=True),
        FieldSpec("database", str, required=True),
        FieldSpec("username", str, required=True),
        FieldSpec("password", str, required=True),
        FieldSpec("ssl", bool, required=False),
    )
)

def connect_to_database(config: dict):
    if not satisfies(config, DatabaseConfigTrait):
        result = explain(config, DatabaseConfigTrait)
        raise ValueError(f"Invalid config: missing {result['missing']}")

    # Config is valid
    return create_connection(**config)
```

### Plugin Validation

```python
PluginTrait = TraitSpec(
    name="Plugin",
    fields=(
        FieldSpec("name", str),
        FieldSpec("version", str),
        FieldSpec("initialize", callable),
        FieldSpec("execute", callable),
    )
)

def load_plugin(plugin_class):
    if not satisfies(plugin_class, PluginTrait):
        raise TypeError("Invalid plugin interface")

    return plugin_class()
```

## Next Steps

- Learn about the [Duck API](duck-api.md) for more ergonomic usage
- Explore [Traits](traits.md) in depth
- Customize behavior with [Type Policies](policies.md)
- Check out more [Examples](../examples/index.md)
