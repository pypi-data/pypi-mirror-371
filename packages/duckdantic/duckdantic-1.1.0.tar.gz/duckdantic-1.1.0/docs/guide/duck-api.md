# Duck API

The Duck API provides an ergonomic interface for duck typing, especially when working with Pydantic models. It makes structural typing as natural as using `isinstance()`.

## Overview

The Duck API centers around the `Duck` factory function that creates duck types from various sources:

```python
from pydantic import BaseModel
from duckdantic import Duck

class User(BaseModel):
    id: int
    name: str
    email: str

# Create a duck type
UserDuck = Duck(User)

# Now use it naturally
data = {"id": 1, "name": "Alice", "email": "alice@example.com"}
assert isinstance(data, UserDuck)  # ✅ Structural check!
```

## Creating Duck Types

### From Pydantic Models

The most common use case:

```python
from pydantic import BaseModel
from duckdantic import Duck

class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool = True

# Create duck type
ProductDuck = Duck(Product)

# Or use generic syntax
ProductDuck = Duck[Product]
```

### From Fields

Create duck types from individual fields:

```python
from pydantic import Field
from duckdantic import Duck

EmailField = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
EmailDuck = Duck(EmailField)

# Check if something has a valid email field
data = {"value": "user@example.com"}
assert isinstance(data, EmailDuck)
```

### From Traits

Use existing trait specifications:

```python
from duckdantic import Duck, TraitSpec, FieldSpec

UserTrait = TraitSpec(
    name="User",
    fields=(
        FieldSpec("id", int),
        FieldSpec("name", str),
    )
)

UserDuck = Duck(UserTrait)
```

## Using Duck Types

### isinstance Checks

The most natural way to use duck types:

```python
# Check dictionaries
user_dict = {"id": 1, "name": "Bob", "email": "bob@example.com"}
assert isinstance(user_dict, UserDuck)

# Check objects
class Customer:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

customer = Customer(2, "Charlie", "charlie@example.com")
assert isinstance(customer, UserDuck)

# Check Pydantic models
from pydantic import BaseModel

class Employee(BaseModel):
    id: int
    name: str
    email: str
    department: str

employee = Employee(id=3, name="David", email="david@example.com", department="IT")
assert isinstance(employee, UserDuck)
```

### Validation Methods

Duck types provide several validation methods:

```python
# Basic validation
if UserDuck.validate(data):
    print("Valid user data!")

# Assertion with custom message
UserDuck.assert_valid(data, "Invalid user data provided")

# Get the underlying trait
trait = UserDuck.trait
print(f"Required fields: {[f.name for f in trait.fields if f.required]}")
```

### Type Conversion

Convert compatible objects to the target model:

```python
# From dictionary
user_dict = {"id": 1, "name": "Alice", "email": "alice@example.com"}
user = UserDuck.convert(user_dict)
print(user)  # User(id=1, name='Alice', email='alice@example.com')

# From another object
class Person:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

person = Person(2, "Bob", "bob@example.com")
user = UserDuck.convert(person)
print(user)  # User(id=2, name='Bob', email='bob@example.com')

# With additional fields
partial = {"id": 3, "name": "Charlie"}
user = UserDuck.convert(partial, email="charlie@example.com")
```

## BaseModel Extensions

Duckdantic extends Pydantic's BaseModel with duck typing methods:

### Class Methods

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# Check if object satisfies model structure
data = {"id": 1, "name": "Alice", "email": "alice@example.com"}
assert User.__duck_validates__(data)

# Convert duck-typed object to model
user = User.__duck_convert__(data)
```

### Convenience Functions

```python
from duckdantic import is_duck_of, as_duck

# Quick check
if is_duck_of(data, User):
    print("It's user-like!")

# Quick conversion
user = as_duck(User, data)
```

## DuckModel Base Class

For enhanced duck typing support, inherit from `DuckModel`:

```python
from duckdantic import DuckModel

class User(DuckModel):
    id: int
    name: str
    email: str

# Get the duck type
UserDuck = User.duck_type

# Check compatibility
data = {"id": 1, "name": "Alice", "email": "alice@example.com"}
assert User.is_duck(data)

# Convert from duck
user = User.from_duck(data)
```

## DuckRootModel

For root models (lists, dicts, etc.):

```python
from typing import List
from duckdantic import DuckRootModel

class UserList(DuckRootModel[List[User]]):
    pass

# Validate list of user-like objects
data = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]

assert UserList.__duck_validates__(data)
users = UserList.from_duck(data)
```

## Custom Policies

Control type checking behavior:

```python
from duckdantic import Duck, TypeCompatPolicy

# Strict policy
strict_policy = TypeCompatPolicy(
    allow_numeric_widening=False,
    allow_optional_widening=False,
)

StrictUserDuck = Duck(User, policy=strict_policy)

# Now int won't satisfy float fields
data = {"id": 1, "name": "Alice", "balance": 100}  # balance is int
assert not isinstance(data, StrictUserDuck)  # If balance should be float
```

## Generic Syntax

Duck supports generic syntax for type hints:

```python
from typing import TypeVar
from duckdantic import Duck

T = TypeVar('T')

def validate_data(data: dict, model: type[T]) -> T:
    """Validate and convert data to model using duck typing."""
    ModelDuck = Duck[model]

    if not isinstance(data, ModelDuck):
        raise ValueError(f"Data doesn't match {model.__name__} structure")

    return ModelDuck.convert(data)

# Usage
user = validate_data({"id": 1, "name": "Alice", "email": "a@b.com"}, User)
```

## Common Patterns

### API Response Handling

```python
from typing import Generic, TypeVar
from pydantic import BaseModel
from duckdantic import Duck, DuckModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T
    error: str | None = None

class User(DuckModel):
    id: int
    name: str

# Create duck type for user response
UserResponseDuck = Duck[APIResponse[User]]

# Validate response
response = {
    "success": True,
    "data": {"id": 1, "name": "Alice"},
    "error": None
}

if isinstance(response, UserResponseDuck):
    user_response = UserResponseDuck.convert(response)
    user = user_response.data
```

### Form Validation

```python
class RegistrationForm(DuckModel):
    username: str
    email: str
    password: str
    confirm_password: str

def process_registration(form_data: dict):
    # Quick validation
    if not RegistrationForm.is_duck(form_data):
        raise ValueError("Invalid registration data")

    # Convert and validate business rules
    form = RegistrationForm.from_duck(form_data)

    if form.password != form.confirm_password:
        raise ValueError("Passwords don't match")

    # Process registration...
```

### Type Bridging

```python
# Convert between similar types from different libraries
class ExternalUser:
    def __init__(self, user_id: int, username: str, user_email: str):
        self.user_id = user_id
        self.username = username
        self.user_email = user_email

class InternalUser(DuckModel):
    id: int
    name: str
    email: str

# Create adapter
def adapt_user(external: ExternalUser) -> InternalUser:
    # Map fields appropriately
    data = {
        "id": external.user_id,
        "name": external.username,
        "email": external.user_email
    }

    # Convert using duck typing
    return InternalUser.from_duck(data)
```

## Performance Tips

1. **Cache Duck Types**: Create once, reuse many times

   ```python
   # Good - create once
   USER_DUCK = Duck(User)

   def validate_users(users: list[dict]):
       return all(isinstance(u, USER_DUCK) for u in users)
   ```

2. **Use Direct Methods**: For hot paths, use model methods directly

   ```python
   # Faster for many checks
   if User.__duck_validates__(data):
       user = User.__duck_convert__(data)
   ```

3. **Batch Validation**: Validate multiple objects together
   ```python
   def validate_batch(items: list[dict], model: type[BaseModel]):
       duck = Duck(model)
       return [item for item in items if isinstance(item, duck)]
   ```

## Next Steps

- Learn about [Traits](traits.md) for more complex requirements
- Explore [Type Policies](policies.md) for customization
- Check out Advanced Topics (coming soon) for optimization
