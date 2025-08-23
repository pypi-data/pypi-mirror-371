# 🦆 Duckdantic

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/duckdantic.svg)](https://pypi.org/project/duckdantic/)
[![Python Version](https://img.shields.io/pypi/pyversions/duckdantic.svg)](https://pypi.org/project/duckdantic/)
[![License](https://img.shields.io/pypi/l/duckdantic.svg)](https://github.com/pr1m8/duckdantic/blob/main/LICENSE.txt)
[![Tests](https://github.com/pr1m8/duckdantic/workflows/tests/badge.svg)](https://github.com/pr1m8/duckdantic/actions)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://pr1m8.github.io/duckdantic/)

**🚀 Structural typing and runtime validation for Python**

*If it walks like a duck and quacks like a duck, then it's probably a duck*

[📚 Documentation](https://pr1m8.github.io/duckdantic/) • [🎯 Examples](https://pr1m8.github.io/duckdantic/examples/) • [📦 PyPI](https://pypi.org/project/duckdantic/)

</div>

---

## 🌟 What is Duckdantic?

**Duckdantic** brings true **structural typing** to Python runtime! Check if objects satisfy interfaces without inheritance, validate data shapes dynamically, and build flexible APIs that work with **any** compatible object.

Perfect for **microservices**, **plugin architectures**, and **polyglot systems** where you need structural compatibility without tight coupling.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🦆 **True Duck Typing** | Runtime structural validation without inheritance |
| ⚡ **High Performance** | Intelligent caching and optimized field normalization |  
| 🔌 **Universal Compatibility** | Works with [Pydantic](https://pydantic.dev/), [dataclasses](https://docs.python.org/3/library/dataclasses.html), [TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict), [attrs](https://www.attrs.org/), and plain objects |
| 🎯 **Flexible Policies** | Customize validation behavior (strict, lenient, coercive) |
| 🏗️ **Protocol Integration** | Drop-in compatibility with Python's [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol) |
| 🔍 **ABC Support** | Use with `isinstance()` and `issubclass()` |
| 🎨 **Ergonomic API** | Clean, intuitive interface with excellent IDE support |

## 📦 Installation

```bash
# Basic installation
pip install duckdantic

# With Pydantic support (recommended)
pip install "duckdantic[pydantic]"

# Development installation
pip install "duckdantic[all]"
```

## 🚀 Quick Start

### The Duck API (Most Popular)

Perfect for **Pydantic** users and modern Python development:

```python
from pydantic import BaseModel
from duckdantic import Duck

# Define your models
class User(BaseModel):
    name: str
    email: str
    age: int
    is_active: bool = True

class Person(BaseModel):
    name: str
    age: int

# Create a structural type
PersonShape = Duck(Person)

# ✅ Structural validation - no inheritance needed!
user = User(name="Alice", email="alice@example.com", age=30)
assert isinstance(user, PersonShape)  # True! User has required Person fields

# 🔄 Convert between compatible types
person = PersonShape.convert(user)  # Person(name="Alice", age=30)
```

### Universal Compatibility

Works with **any** Python object:

```python
from dataclasses import dataclass
from typing import TypedDict
from duckdantic import Duck

# Works with dataclasses
@dataclass
class DataPerson:
    name: str
    age: int

# Works with TypedDict
class DictPerson(TypedDict):
    name: str
    age: int

# Works with plain objects
class PlainPerson:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

# One duck type validates them all!
PersonShape = Duck.from_fields({"name": str, "age": int})

# ✅ All of these work
assert isinstance(DataPerson("Bob", 25), PersonShape)
assert isinstance(DictPerson(name="Charlie", age=35), PersonShape)  
assert isinstance(PlainPerson("Diana", 28), PersonShape)
```

### Advanced: Trait-Based Validation

For complex structural requirements:

```python
from duckdantic import TraitSpec, FieldSpec, satisfies

# Define a complex trait
APIResponse = TraitSpec(
    name="APIResponse",
    fields=(
        FieldSpec("status", int, required=True),
        FieldSpec("data", dict, required=True),
        FieldSpec("message", str, required=False),
        FieldSpec("timestamp", str, required=False),
    )
)

# Validate any object structure
response1 = {"status": 200, "data": {"users": []}}
response2 = {"status": 404, "data": {}, "message": "Not found"}

assert satisfies(response1, APIResponse)  # ✅ 
assert satisfies(response2, APIResponse)  # ✅
```

### Method Validation

Ensure objects implement required methods:

```python
from duckdantic import MethodSpec, methods_satisfy

# Define method requirements (like typing.Protocol)
Drawable = [
    MethodSpec("draw", params=[int, int], returns=None),
    MethodSpec("get_bounds", params=[], returns=tuple),
]

class Circle:
    def draw(self, x: int, y: int) -> None:
        print(f"Drawing circle at ({x}, {y})")
    
    def get_bounds(self) -> tuple:
        return (0, 0, 10, 10)

assert methods_satisfy(Circle, Drawable)  # ✅
```

## 🎯 Common Use Cases

### 🌐 Microservices & APIs

```python
from duckdantic import Duck
from fastapi import FastAPI
from pydantic import BaseModel

class CreateUserRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: str

# Ensure response compatibility across services
ResponseShape = Duck(UserResponse)

app = FastAPI()

@app.post("/users/")
def create_user(request: CreateUserRequest):
    # Any object with the right shape works
    response = build_user_response(request)  # From any source
    assert isinstance(response, ResponseShape)  # Validation
    return response
```

### 🔌 Plugin Systems

```python
from duckdantic import Duck

# Define plugin interface
class PluginInterface:
    name: str
    version: str
    def execute(self, data: dict) -> dict: ...

PluginShape = Duck(PluginInterface)

# Load plugins from anywhere
def load_plugin(plugin_class):
    if isinstance(plugin_class(), PluginShape):
        return plugin_class()
    raise ValueError("Invalid plugin structure")
```

### 🧪 Testing & Mocking

```python
from duckdantic import Duck

ProductionModel = Duck(YourProductionClass)

# Create test doubles that satisfy production interfaces
class MockService:
    def __init__(self):
        self.required_field = "test"
        self.another_field = 42

mock = MockService()
assert isinstance(mock, ProductionModel)  # ✅ Valid test double
```

## 🔗 Related Projects

| Project | Relationship | When to Use |
|---------|--------------|-------------|
| [**Pydantic**](https://pydantic.dev/) | 🤝 **Perfect Companion** | Use Pydantic for data validation, Duckdantic for structural typing |
| [**typing.Protocol**](https://docs.python.org/3/library/typing.html#typing.Protocol) | 🔄 **Runtime Alternative** | Protocols are static, Duckdantic is runtime + dynamic |
| [**attrs**](https://www.attrs.org/) | ✅ **Fully Compatible** | Define classes with attrs, validate with Duckdantic |
| [**dataclasses**](https://docs.python.org/3/library/dataclasses.html) | ✅ **Fully Compatible** | Built-in support for dataclass validation |
| [**TypedDict**](https://docs.python.org/3/library/typing.html#typing.TypedDict) | ✅ **Fully Compatible** | Validate dictionary structures dynamically |

## 🏗️ Architecture Patterns

### Hexagonal Architecture
```python
# Define port interfaces with Duck types
UserRepositoryPort = Duck.from_methods({
    "save": (User,) -> User,
    "find_by_id": (int,) -> Optional[User],
})

# Any implementation that matches the structure works
class SQLUserRepository:
    def save(self, user: User) -> User: ...
    def find_by_id(self, user_id: int) -> Optional[User]: ...

assert isinstance(SQLUserRepository(), UserRepositoryPort)  # ✅
```

### CQRS Pattern
```python
# Command/Query interfaces as Duck types
Command = Duck.from_fields({"command_id": str, "timestamp": datetime})
Query = Duck.from_fields({"query_id": str, "filters": dict})

# Any object with the right shape is valid
CreateUserCommand = {"command_id": "123", "timestamp": datetime.now(), "user_data": {...}}
assert isinstance(CreateUserCommand, Command)  # ✅
```

## 📊 Performance

Duckdantic is built for **production performance**:

- **Intelligent caching**: Field analysis cached per type
- **Lazy evaluation**: Only validates what's needed
- **Zero-copy operations**: Minimal object creation overhead
- **Optimized for common patterns**: Special handling for Pydantic/dataclasses

```python
# Benchmark: 1M validations
import timeit
from duckdantic import Duck

PersonShape = Duck.from_fields({"name": str, "age": int})
test_obj = {"name": "test", "age": 25}

time_taken = timeit.timeit(
    lambda: isinstance(test_obj, PersonShape),
    number=1_000_000
)
print(f"1M validations: {time_taken:.2f}s")  # ~0.5s on modern hardware
```

## 🛠️ Advanced Configuration

### Custom Validation Policies

```python
from duckdantic import Duck, ValidationPolicy

# Strict policy: exact type matching
strict_duck = Duck(MyModel, policy=ValidationPolicy.STRICT)

# Lenient policy: duck typing with coercion
lenient_duck = Duck(MyModel, policy=ValidationPolicy.LENIENT)

# Custom policy: your own rules
class CustomPolicy(ValidationPolicy):
    def validate_field(self, value, expected_type):
        # Your custom validation logic
        return custom_validation(value, expected_type)

custom_duck = Duck(MyModel, policy=CustomPolicy())
```

### Integration with Type Checkers

```python
from typing import TYPE_CHECKING
from duckdantic import Duck

if TYPE_CHECKING:
    # Static type checking with Protocol
    from typing import Protocol
    
    class PersonProtocol(Protocol):
        name: str
        age: int
else:
    # Runtime validation with Duck
    PersonProtocol = Duck.from_fields({"name": str, "age": int})

# Works with both mypy and runtime!
def process_person(person: PersonProtocol) -> str:
    return f"{person.name} is {person.age} years old"
```

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| [📖 **Getting Started**](https://pr1m8.github.io/duckdantic/getting-started/) | Complete setup and basic usage guide |
| [🎯 **Examples**](https://pr1m8.github.io/duckdantic/examples/) | Real-world usage patterns and recipes |
| [🔧 **API Reference**](https://pr1m8.github.io/duckdantic/api/) | Complete API documentation |
| [🏗️ **Architecture Guide**](https://pr1m8.github.io/duckdantic/guide/architecture/) | Design patterns and best practices |
| [⚡ **Performance Guide**](https://pr1m8.github.io/duckdantic/guide/performance/) | Optimization tips and benchmarks |

## 🤝 Contributing

We love contributions! Duckdantic is built by the community, for the community.

```bash
# Quick setup
git clone https://github.com/pr1m8/duckdantic.git
cd duckdantic
pip install -e ".[dev]"
pytest  # Run tests
```

See our [**Contributing Guide**](CONTRIBUTING.md) for detailed instructions.

## 🎉 Community

- 🐛 **Found a bug?** [Open an issue](https://github.com/pr1m8/duckdantic/issues)
- 💡 **Have an idea?** [Start a discussion](https://github.com/pr1m8/duckdantic/discussions)
- 📖 **Need help?** Check our [documentation](https://pr1m8.github.io/duckdantic/)
- 🌟 **Like the project?** Give us a star on [GitHub](https://github.com/pr1m8/duckdantic)!

## 📄 License

Licensed under the **MIT License** - see [LICENSE](LICENSE.txt) for details.

## 🙏 Acknowledgments

- **TypeScript** and **Go interfaces** for structural typing inspiration
- **[Pydantic](https://pydantic.dev/)** for showing how beautiful Python validation can be
- **[Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol)** for static structural typing patterns
- **The Python community** for embracing duck typing as a core principle

---

<div align="center">

**"In the face of ambiguity, refuse the temptation to guess."**  
*— The Zen of Python*

**Duckdantic: Where structure meets flexibility** 🦆✨

</div>