# Core Concepts

Understanding these core concepts will help you make the most of Duckdantic.

## Structural Typing vs Nominal Typing

### Nominal Typing

Traditional object-oriented programming uses **nominal typing** - types are compatible based on their names and inheritance relationships:

```python
class Animal:
    pass

class Dog(Animal):
    pass

# Dog is an Animal because it inherits from Animal
isinstance(Dog(), Animal)  # True
```

### Structural Typing

Duckdantic uses **structural typing** - types are compatible based on their structure:

```python
from duckdantic import TraitSpec, FieldSpec, satisfies

# Define structure
HasName = TraitSpec(
    name="HasName",
    fields=(FieldSpec("name", str, required=True),)
)

# Any object with a 'name' field satisfies the trait
class Person:
    def __init__(self, name: str):
        self.name = name

class Company:
    def __init__(self, name: str):
        self.name = name

# Both satisfy HasName despite no inheritance relationship
assert satisfies(Person("Alice"), HasName)
assert satisfies(Company("ACME"), HasName)
```

## Traits

A **trait** is a specification of structural requirements. It defines:

- What fields an object must have
- What types those fields should be
- Whether fields are required or optional

### Creating Traits

```python
from duckdantic import TraitSpec, FieldSpec

UserTrait = TraitSpec(
    name="User",  # Name for debugging/display
    fields=(
        FieldSpec("id", int, required=True),
        FieldSpec("email", str, required=True),
        FieldSpec("active", bool, required=False),
    ),
    metadata={"version": "1.0"}  # Optional metadata
)
```

### Trait Composition

Traits can be combined using set operations:

```python
from duckdantic import union, intersect, minus

# Union: satisfies either trait
FlexibleUser = union(UserTrait, GuestTrait)

# Intersection: must satisfy both traits
AuthenticatedUser = intersect(UserTrait, HasTokenTrait)

# Minus: remove fields
PublicUser = minus(UserTrait, ["email", "password"])
```

## Fields

Fields are the building blocks of traits:

```python
FieldSpec(
    name="age",           # Field name
    typ=int,             # Expected type
    required=True,       # Is it required?
    accept_alias=True,   # Accept aliases?
    check_types=True,    # Enforce type checking?
    custom_matcher=None  # Custom type matcher
)
```

### Field Types

Fields can have any Python type:

- **Primitives**: `int`, `str`, `bool`, `float`
- **Collections**: `list`, `dict`, `set`, `tuple`
- **Generics**: `List[int]`, `Dict[str, Any]`, `Optional[str]`
- **Custom classes**: Any Python class

### Required vs Optional

- **Required fields** must be present for satisfaction
- **Optional fields** may be absent without failing validation

## Type Checking

Duckdantic performs intelligent type checking:

### Basic Type Checking

```python
from duckdantic import TraitSpec, FieldSpec, satisfies

AgeTrait = TraitSpec(
    name="HasAge",
    fields=(FieldSpec("age", int, required=True),)
)

# Exact type match
assert satisfies({"age": 25}, AgeTrait)

# Type mismatch
assert not satisfies({"age": "25"}, AgeTrait)
```

### Numeric Widening

By default, numeric types can widen (int → float):

```python
PriceTrait = TraitSpec(
    name="HasPrice",
    fields=(FieldSpec("price", float, required=True),)
)

# Int satisfies float requirement
assert satisfies({"price": 100}, PriceTrait)
```

### Subclass Acceptance

Subclasses are accepted by default:

```python
class Animal:
    pass

class Dog(Animal):
    pass

PetTrait = TraitSpec(
    name="HasPet",
    fields=(FieldSpec("pet", Animal, required=True),)
)

# Dog satisfies Animal requirement
assert satisfies({"pet": Dog()}, PetTrait)
```

## Type Policies

Policies control how types are compared:

```python
from duckdantic import TypeCompatPolicy, satisfies

# Strict policy - exact matches only
strict = TypeCompatPolicy(
    allow_numeric_widening=False,
    allow_optional_widening=False,
    container_origin_mode="strict"
)

# Check with custom policy
satisfies(obj, trait, policy=strict)
```

### Policy Options

- `allow_numeric_widening`: Accept int where float is expected
- `allow_optional_widening`: Accept T where Optional[T] is expected
- `desired_union`: How to handle Union types on the desired side
- `actual_union`: How to handle Union types on the actual side
- `container_origin_mode`: How strictly to check container types
- `annotated_handling`: How to handle Annotated types
- `literal_mode`: How to handle Literal types
- `alias_mode`: How to handle field aliases

## Aliases

Fields can have aliases for flexibility:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: int = Field(alias="id")
    username: str = Field(alias="name")

# Trait can match by alias
IdTrait = TraitSpec(
    name="HasId",
    fields=(FieldSpec("id", int, required=True),)
)

# Matches 'user_id' field via 'id' alias
user = User(id=1, name="alice")
assert satisfies(user, IdTrait)
```

## Caching

Duckdantic caches normalization results for performance:

```python
from duckdantic import get_cache_stats, clear_cache

# Check cache performance
stats = get_cache_stats()
print(f"Cache hit rate: {stats['hits'] / (stats['hits'] + stats['misses']):.2%}")

# Clear cache if needed
clear_cache()
```

## The Duck API

The Duck API provides a more Pythonic interface:

```python
from duckdantic import Duck
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str

# Create a duck type
UserDuck = Duck(User)

# Use like a regular type
isinstance(obj, UserDuck)  # Structural check
issubclass(cls, UserDuck)  # Class check
```

### Duck Type Methods

- `UserDuck.satisfies(obj)`: Check satisfaction
- `UserDuck.explain(obj)`: Get detailed feedback
- `UserDuck.convert(obj)`: Convert compatible objects
- `UserDuck.validate(obj)`: Validate and convert

## Performance Considerations

### Normalization Cost

Field extraction is the most expensive operation. Duckdantic caches results based on object "shape":

- Classes are cached by type
- Dictionaries are cached by their keys
- Instances delegate to their class cache

### Best Practices

1. **Reuse traits** - Create traits once and reuse them
2. **Use the cache** - Let the built-in cache work for you
3. **Batch checks** - Check multiple objects against the same trait
4. **Simple types** - Prefer simple types over complex generics when possible

## Integration Patterns

### With Type Checkers

Duckdantic complements static type checkers:

```python
from typing import Protocol
from duckdantic import TraitSpec, FieldSpec

# Static protocol
class UserProtocol(Protocol):
    name: str
    email: str

# Runtime trait
UserTrait = TraitSpec(
    name="User",
    fields=(
        FieldSpec("name", str, required=True),
        FieldSpec("email", str, required=True),
    )
)

# Use both for complete type safety
def process_user(user: UserProtocol) -> None:
    assert satisfies(user, UserTrait)  # Runtime check
    # ... process user
```

### With Pydantic

Duckdantic works seamlessly with Pydantic:

```python
from pydantic import BaseModel
from duckdantic import Duck

class UserModel(BaseModel):
    name: str
    email: str

# Create duck type from Pydantic model
UserDuck = Duck(UserModel)

# Check any object
data = {"name": "Bob", "email": "bob@example.com"}
if isinstance(data, UserDuck):
    user = UserModel(**data)  # Safe to construct
```
