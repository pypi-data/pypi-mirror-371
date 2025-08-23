# Duckdantic 🦆

[![PyPI](https://img.shields.io/pypi/v/duckdantic.svg)](https://pypi.org/project/duckdantic/)
[![Python Version](https://img.shields.io/pypi/pyversions/duckdantic.svg)](https://pypi.org/project/duckdantic/)
[![License](https://img.shields.io/pypi/l/duckdantic.svg)](https://github.com/pr1m8/duckdantic/blob/main/LICENSE.txt)
[![Tests](https://github.com/pr1m8/duckdantic/workflows/tests/badge.svg)](https://github.com/pr1m8/duckdantic/actions)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://pr1m8.github.io/duckdantic/)

**Duckdantic** is a Python library for flexible structural typing and runtime validation. It provides a powerful way to define structural types (traits) and check whether objects satisfy them at runtime, without requiring inheritance or type annotations.

## ✨ Features

- 🦆 **True Duck Typing**: Check object structures at runtime without inheritance
- 🏗️ **Trait-Based Validation**: Define reusable structural requirements
- 🔧 **Framework Agnostic**: Works with Pydantic, dataclasses, TypedDict, and plain objects
- 🎯 **Flexible Policies**: Customize type checking behavior to your needs
- 🚀 **High Performance**: Intelligent caching and optimized field normalization
- 🎨 **Intuitive API**: Clean, Pythonic interface with excellent IDE support
- 🔌 **ABC Integration**: Use traits with `isinstance()` and `issubclass()`

## 📦 Installation

```bash
pip install duckdantic
```

For Pydantic support:

```bash
pip install "duckdantic[pydantic]"
```

## 🚀 Quick Start

### Basic Usage

```python
from duckdantic import TraitSpec, FieldSpec, satisfies

# Define a trait
PersonTrait = TraitSpec(
    name="Person",
    fields=(
        FieldSpec("name", str, required=True),
        FieldSpec("age", int, required=True),
    )
)

# Check if objects satisfy the trait
class Employee:
    def __init__(self, name: str, age: int, employee_id: str):
        self.name = name
        self.age = age
        self.employee_id = employee_id

emp = Employee("Alice", 30, "EMP001")
assert satisfies(emp, PersonTrait)  # ✅ True - has required fields
```

### Duck API (Recommended)

The Duck API provides a more ergonomic interface, especially when working with Pydantic models:

```python
from pydantic import BaseModel
from duckdantic import Duck

class User(BaseModel):
    name: str
    email: str
    age: int

class Person(BaseModel):
    name: str
    age: int

# Create a duck type from a Pydantic model
PersonDuck = Duck(Person)

# Check if instances satisfy the duck type
user = User(name="Bob", email="bob@example.com", age=25)
assert isinstance(user, PersonDuck)  # ✅ True - has required fields

# Convert between compatible types
person = PersonDuck.convert(user)  # Creates Person(name="Bob", age=25)
```

### Method Checking

```python
from duckdantic import MethodSpec, methods_satisfy

# Define method requirements
DrawableMethods = [
    MethodSpec("draw", params=[int, int], returns=None),
    MethodSpec("get_color", params=[], returns=str),
]

class Circle:
    def draw(self, x: int, y: int) -> None:
        pass

    def get_color(self) -> str:
        return "red"

assert methods_satisfy(Circle, DrawableMethods)  # ✅ True
```

### ABC Integration

```python
from duckdantic import TraitSpec, FieldSpec, abc_for

# Define a trait
ConfigTrait = TraitSpec(
    name="Config",
    fields=(
        FieldSpec("host", str),
        FieldSpec("port", int),
    )
)

# Create an ABC from the trait
ConfigABC = abc_for(ConfigTrait)

# Use with isinstance
@ConfigABC.register
class ServerConfig:
    host: str = "localhost"
    port: int = 8080

assert isinstance(ServerConfig(), ConfigABC)  # ✅ True
```

## 🎯 Use Cases

- **API Validation**: Ensure objects have required fields before processing
- **Plugin Systems**: Define interfaces without requiring inheritance
- **Type Bridges**: Convert between similar types from different libraries
- **Testing**: Create test doubles that satisfy production interfaces
- **Configuration**: Validate configuration objects from various sources

## 📚 Documentation

For comprehensive documentation, visit [https://pr1m8.github.io/duckdantic/](https://pr1m8.github.io/duckdantic/)

- [Getting Started Guide](https://pr1m8.github.io/duckdantic/getting-started/)
- [API Reference](https://pr1m8.github.io/duckdantic/api/)
- [Examples](https://pr1m8.github.io/duckdantic/examples/)
- [Advanced Usage](https://pr1m8.github.io/duckdantic/guide/advanced/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## 🙏 Acknowledgments

- Inspired by structural typing concepts from TypeScript and Go interfaces
- Built to complement Pydantic's excellent runtime validation
- Thanks to all contributors and users of the library
