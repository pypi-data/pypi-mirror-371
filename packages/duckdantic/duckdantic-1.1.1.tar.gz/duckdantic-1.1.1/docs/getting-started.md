# Getting Started

This guide will help you get up and running with Duckdantic in just a few minutes.

## Installation

Install Duckdantic using pip:

```bash
pip install duckdantic
```

If you're using Pydantic, install with the optional dependency:

```bash
pip install "duckdantic[pydantic]"
```

## Core Concepts

Before diving in, let's understand the key concepts:

### Traits

A **trait** is a structural type definition that describes what fields an object should have. Think of it as a "shape" that objects can satisfy.

### Fields

**Fields** define the individual attributes that make up a trait, including their types and whether they're required.

### Satisfaction

An object **satisfies** a trait if it has all the required fields with compatible types.

## Your First Trait

Let's create a simple trait and check if objects satisfy it:

```python
from duckdantic import TraitSpec, FieldSpec, satisfies

# Define a trait for anything that has a name and age
PersonTrait = TraitSpec(
    name="Person",
    fields=(
        FieldSpec("name", str, required=True),
        FieldSpec("age", int, required=True),
    )
)

# Create different objects
class Employee:
    def __init__(self, name: str, age: int, department: str):
        self.name = name
        self.age = age
        self.department = department

employee = Employee("Alice", 30, "Engineering")

# Check satisfaction
print(satisfies(employee, PersonTrait))  # True
```

## Working with Different Object Types

Duckdantic works with any Python object:

### Dictionaries

```python
person_dict = {"name": "Bob", "age": 25}
assert satisfies(person_dict, PersonTrait)
```

### Dataclasses

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

user = User("Charlie", 35, "charlie@example.com")
assert satisfies(user, PersonTrait)
```

### Pydantic Models

```python
from pydantic import BaseModel

class Customer(BaseModel):
    name: str
    age: int
    subscription: str

customer = Customer(name="David", age=40, subscription="premium")
assert satisfies(customer, PersonTrait)
```

## The Duck API

For a more intuitive interface, especially with Pydantic, use the Duck API:

```python
from pydantic import BaseModel
from duckdantic import Duck

# Define your models
class User(BaseModel):
    id: int
    name: str
    email: str

class Person(BaseModel):
    name: str
    email: str

# Create a duck type
PersonDuck = Duck(Person)

# Use with isinstance
user = User(id=1, name="Eve", email="eve@example.com")
assert isinstance(user, PersonDuck)  # True!

# Convert between types
person = PersonDuck.convert(user)
print(person)  # Person(name='Eve', email='eve@example.com')
```

## Optional Fields

Not all fields need to be required:

```python
ProfileTrait = TraitSpec(
    name="Profile",
    fields=(
        FieldSpec("username", str, required=True),
        FieldSpec("bio", str, required=False),  # Optional
        FieldSpec("avatar", str, required=False),  # Optional
    )
)

# Minimal object still satisfies
minimal = {"username": "frank"}
assert satisfies(minimal, ProfileTrait)

# Object with all fields also satisfies
complete = {
    "username": "grace",
    "bio": "Software developer",
    "avatar": "https://example.com/avatar.jpg"
}
assert satisfies(complete, ProfileTrait)
```

## Type Flexibility

By default, Duckdantic is pragmatic about types:

```python
NumberTrait = TraitSpec(
    name="Numeric",
    fields=(FieldSpec("value", float, required=True),)
)

# Int satisfies float requirement (numeric widening)
int_obj = {"value": 42}
assert satisfies(int_obj, NumberTrait)

# But string doesn't
str_obj = {"value": "42"}
assert not satisfies(str_obj, NumberTrait)
```

## Getting Detailed Feedback

Use `explain()` to understand why validation fails:

```python
from duckdantic import explain

incomplete = {"username": "henry"}  # Missing required email

result = explain(incomplete, UserTrait)
if not result["ok"]:
    print("Missing fields:", result["missing"])
    print("Type conflicts:", result["type_conflicts"])
```

## Method Checking

Check if objects have the right methods:

```python
from duckdantic import MethodSpec, methods_satisfy

# Define required methods
SaveableMethods = [
    MethodSpec("save", params=[], returns=bool),
    MethodSpec("load", params=[str], returns=None),
]

class Document:
    def save(self) -> bool:
        return True

    def load(self, path: str) -> None:
        pass

assert methods_satisfy(Document(), SaveableMethods)
```

## Next Steps

Now that you understand the basics, explore:

- [Duck API Guide](guide/duck-api.md) - Learn about the ergonomic Duck interface
- [Traits in Depth](guide/traits.md) - Advanced trait features
- [Type Policies](guide/policies.md) - Customize type checking behavior
- [Examples](examples/index.md) - Real-world use cases

## Common Patterns

### API Response Validation

```python
APIResponseTrait = TraitSpec(
    name="APIResponse",
    fields=(
        FieldSpec("status", str, required=True),
        FieldSpec("data", dict, required=True),
        FieldSpec("error", str, required=False),
    )
)

# Validate API responses
response = {"status": "success", "data": {"user_id": 123}}
assert satisfies(response, APIResponseTrait)
```

### Plugin Interfaces

```python
PluginTrait = TraitSpec(
    name="Plugin",
    fields=(
        FieldSpec("name", str, required=True),
        FieldSpec("version", str, required=True),
    )
)

# Ensure plugins have required fields
def load_plugin(plugin):
    if not satisfies(plugin, PluginTrait):
        raise ValueError("Invalid plugin structure")
    # ... load the plugin
```

### Configuration Validation

```python
ConfigTrait = TraitSpec(
    name="Config",
    fields=(
        FieldSpec("host", str, required=True),
        FieldSpec("port", int, required=True),
        FieldSpec("debug", bool, required=False),
    )
)

# Validate configs from various sources
config = load_config_from_file()
if not satisfies(config, ConfigTrait):
    raise ValueError("Invalid configuration")
```
