# Welcome to Duckdantic

<div align="center">
    <h1>🦆 Duckdantic</h1>
    <p><strong>Flexible structural typing and runtime validation for Python</strong></p>
</div>

---

## What is Duckdantic?

Duckdantic is a Python library that brings true duck typing to runtime validation. It allows you to define structural types (called **traits**) and check whether objects satisfy them, regardless of their actual type or inheritance hierarchy.

> "If it walks like a duck and quacks like a duck, then it must be a duck"

With Duckdantic, you can verify this programmatically!

## Key Features

### 🦆 True Duck Typing

Check if objects have the right structure, not the right type. Works with any Python object - Pydantic models, dataclasses, TypedDict, plain classes, or even dictionaries.

### 🏗️ Trait-Based Design

Define reusable structural requirements that can be mixed, matched, and composed. Think of traits as "interfaces" that don't require inheritance.

### 🚀 High Performance

Intelligent caching and optimized field normalization ensure your runtime checks don't slow down your application.

### 🎯 Flexible Policies

Fine-tune how types are compared with policies that control subclass acceptance, numeric widening, literal handling, and more.

### 🔌 Seamless Integration

Works perfectly with existing Python typing features. Use traits with `isinstance()`, create ABCs, and integrate with your favorite frameworks.

## Quick Example

```python
from duckdantic import TraitSpec, FieldSpec, satisfies

# Define what a "User" should look like
UserTrait = TraitSpec(
    name="User",
    fields=(
        FieldSpec("id", int, required=True),
        FieldSpec("email", str, required=True),
        FieldSpec("name", str, required=False),
    )
)

# Any object with the right fields satisfies the trait
class Customer:
    def __init__(self, id: int, email: str, company: str):
        self.id = id
        self.email = email
        self.company = company

customer = Customer(1, "alice@example.com", "ACME Corp")
assert satisfies(customer, UserTrait)  # ✅ It's user-like!

# Even dictionaries work
user_dict = {"id": 2, "email": "bob@example.com"}
assert satisfies(user_dict, UserTrait)  # ✅ Also user-like!
```

## Why Duckdantic?

### The Problem

Python's dynamic typing is powerful, but sometimes you need to ensure objects have certain fields or methods at runtime. Traditional approaches require:

- **Inheritance**: Forces rigid hierarchies
- **Type annotations**: Only checked by static analyzers
- **Manual validation**: Tedious and error-prone

### The Solution

Duckdantic provides a clean, Pythonic way to:

- ✅ Validate object structures at runtime
- ✅ Bridge between different frameworks (Pydantic ↔ dataclasses ↔ TypedDict)
- ✅ Define flexible interfaces without inheritance
- ✅ Build plugin systems with runtime guarantees
- ✅ Test with confidence using structural assertions

## Installation

```bash
pip install duckdantic
```

For Pydantic support:

```bash
pip install "duckdantic[pydantic]"
```

## Next Steps

<div class="grid cards" markdown>

- :material-rocket-launch: **[Getting Started](getting-started.md)**

  ***

  Learn the basics and start using Duckdantic in your projects

- :material-book-open: **[User Guide](guide/index.md)**

  ***

  Comprehensive guide to all Duckdantic features

- :material-code-braces: **[API Reference](api/index.md)**

  ***

  Complete API documentation with examples

- :material-test-tube: **[Examples](examples/index.md)**

  ***

  Real-world examples and use cases

</div>

## Project Links

- [GitHub Repository](https://github.com/pr1m8/duckdantic)
- [PyPI Package](https://pypi.org/project/duckdantic/)
- [Issue Tracker](https://github.com/pr1m8/duckdantic/issues)
- [Discussions](https://github.com/pr1m8/duckdantic/discussions)
