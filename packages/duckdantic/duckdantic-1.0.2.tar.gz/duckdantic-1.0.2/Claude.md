# Duckdantic Project Documentation

## Project Overview

Duckdantic is a structural typing library that provides runtime type checking and trait-based validation for Python. It enables duck typing patterns while maintaining type safety through a declarative trait specification system, designed to work with (and beyond) Pydantic v2.

### Core Philosophy

- **Duck typing with safety**: If it walks like a duck and quacks like a duck, verify it actually is a duck at runtime
- **Framework agnostic**: Works with Pydantic, dataclasses, TypedDict, attrs, plain classes, and mappings
- **Zero dependencies**: Duck-types Pydantic's interfaces without importing it directly
- **Policy-based flexibility**: Configurable type compatibility rules for different use cases

## Current State Analysis

### Version and Status

- **Version**: 0.1.dev4 (early development)
- **Python**: 3.9+ required
- **Main Dependencies**: None required, optional support for pydantic, attrs

### Completed Components

1. **Core Infrastructure** ✅
   - Field normalization system (`normalize.py`, `fields.py`)
   - Trait specification system (`traits.py`)
   - Type comparison engine (`comparer.py`, `policy.py`)
   - Matching and validation (`match.py`)
   - Set operations algebra (`algebra.py`)
   - Registry system (`registry.py`)
   - Caching layer (`cache.py`, `shapes.py`)

2. **Provider System** ✅
   - Base provider protocol
   - Providers for: Pydantic v2, dataclasses, TypedDict, attrs, plain classes, mappings
   - Auto-detection of shape types

3. **Testing** ✅
   - Comprehensive test suite with 30+ test files
   - Property-based testing with Hypothesis
   - Coverage of edge cases and complex scenarios

### Missing/Incomplete Items

1. **Documentation** 🔴
   - README.md shows template content from "hatch_test"
   - No API documentation or Sphinx setup
   - No examples directory or quickstart guide
   - Missing contribution guidelines

2. **Build/Development Tools** 🟡
   - Per TODO.md: sqlparse, sqlfluff, graphql versions need configuration
   - cliff, towncrier, cz tools need setup
   - Trunk configuration needs fixing

3. **PR Bundle Integration** 🔴
   - Methods API needs integration (`build/methods.py`)
   - ABC adapter needs integration (`adapters/abc.py`)
   - Provider updates needed (add `computed()` method)
   - Associated tests need integration

4. **Package Organization** 🟡
   - Missing `__init__.py` files in sub-packages
   - Need to create `build/` and `adapters/` directories
   - Imports in PR bundle need path updates

## Architecture Overview

### Module Structure

```
src/duckdantic/
├── __init__.py          # Public API exports
├── __about__.py         # Version info
├── fields.py            # FieldView data structure
├── normalize.py         # Field extraction/normalization
├── traits.py            # TraitSpec and FieldSpec definitions
├── match.py             # Main satisfies() and explain() functions
├── comparer.py          # Type comparison logic
├── policy.py            # Type compatibility policies
├── algebra.py           # Set operations (union, intersect, minus)
├── compare.py           # Trait relationship analysis
├── registry.py          # Named trait storage
├── cache.py             # Memoization utilities
├── shapes.py            # Shape detection and tokens
├── naming.py            # Auto-naming utilities
├── extras.py            # Optional feature flags
├── providers/           # Shape-specific adapters
│   ├── base.py          # Provider protocol
│   ├── pydantic_v2.py   # Pydantic v2 support
│   ├── dataclass.py     # Dataclass support
│   ├── typeddict.py     # TypedDict support
│   ├── attrs.py         # Attrs support
│   ├── plainclass.py    # Plain class support
│   └── mapping.py       # Dict/mapping support
├── build/               # [TO CREATE] Builder patterns
│   └── methods.py       # [TO ADD] Method signature checking
└── adapters/            # [TO CREATE] Integration adapters
    └── abc.py           # [TO ADD] ABC runtime creation
```

### Key Design Patterns

1. **Provider Pattern**: Extensible adapters for different data structures
2. **Policy Objects**: Configurable behavior through policy classes
3. **Immutable Data**: Frozen dataclasses for thread safety
4. **Protocol-Based Design**: Clean abstractions using Python protocols
5. **Memoization**: Performance optimization through caching

## Integration Tasks

### Phase 1: Directory Structure

1. Create missing directories:
   - `src/duckdantic/build/`
   - `src/duckdantic/adapters/`
   - Add `__init__.py` files to new directories

### Phase 2: PR Bundle Integration

1. **Methods API Integration**:
   - Copy `methods.py` to `src/duckdantic/build/`
   - Update imports from `structdantic` to `duckdantic`
   - Fix relative imports

2. **ABC Adapter Integration**:
   - Copy `abc.py` to `src/duckdantic/adapters/`
   - Update imports
   - Add exports to main `__init__.py`

3. **Provider Updates**:
   - Add `computed()` method to all providers (returns empty dict)
   - Ensure compatibility with existing code

4. **Test Integration**:
   - Copy test files with updated imports
   - Verify all tests pass

### Phase 3: Documentation

1. **Update README.md** with:
   - Project description and philosophy
   - Installation instructions
   - Quick start examples
   - Feature overview

2. **Create docs/ directory** with:
   - API reference
   - Tutorial/guide
   - Advanced usage examples
   - Architecture documentation

3. **Setup Sphinx** for API documentation generation

### Phase 4: Development Tools

1. Configure missing tools per TODO.md
2. Setup pre-commit hooks
3. Configure CI/CD pipelines
4. Add code coverage reporting

## Code Style Guidelines

### Documentation

- Use Google-style docstrings for all public APIs
- Include Args, Returns, Raises, and Examples sections
- Module-level docstrings explaining purpose and main classes

### Naming Conventions

- Classes: PascalCase (e.g., `TraitSpec`, `FieldView`)
- Functions: snake_case (e.g., `satisfies`, `methods_explain`)
- Constants: UPPER_SNAKE_CASE
- Private: Leading underscore (e.g., `_internal_function`)

### Type Hints

- Always include type hints for function signatures
- Use `typing` module for complex types
- Prefer `Union[X, None]` over `Optional[X]` for clarity
- Use protocols for extensibility points

### Testing

- Simple function-based tests with `test_` prefix
- Direct assertions without complex fixtures
- Focus on behavior, not implementation
- One test file per module/feature

## API Quick Reference

### Core Functions

```python
from duckdantic import satisfies, explain, TraitSpec, FieldSpec

# Check if object satisfies trait
result = satisfies(obj, trait_spec)

# Get detailed explanation
explanation = explain(obj, trait_spec)
```

### Trait Building

```python
# Define a trait
user_trait = TraitSpec(
    fields=[
        FieldSpec(name="id", type=int, required=True),
        FieldSpec(name="email", type=str, required=True),
        FieldSpec(name="name", type=str, required=False)
    ]
)
```

### Set Operations

```python
from duckdantic import intersect, union, minus

# Combine traits
combined = intersect(trait1, trait2)
either = union(trait1, trait2)
reduced = minus(trait1, ["field_to_remove"])
```

### Registry

```python
from duckdantic import Registry

registry = Registry()
registry.add("User", user_trait)
compatible = registry.compatible_traits(my_object)
```

## Common Use Cases

1. **Runtime validation of API responses**
2. **Duck-typing across different data structures**
3. **Structural subtyping without inheritance**
4. **Dynamic trait composition**
5. **Framework-agnostic data validation**

## Performance Considerations

- Field normalization is cached per class
- Shape detection uses stable tokens for consistency
- Type comparison can be expensive for deep structures
- Consider using `strict_mode=False` for better performance

## Future Enhancements

1. **Computed fields support** (stub exists in providers)
2. **Async validation support**
3. **Custom validator functions**
4. **Performance profiling tools**
5. **Integration with type checkers (mypy plugin)**
6. **Serialization/deserialization helpers**

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure optional dependencies are installed for specific providers
2. **Type mismatches**: Check policy configuration for numeric widening, literal handling
3. **Performance**: Enable caching, consider relaxing type policies
4. **Alias conflicts**: Configure alias resolution mode appropriately

### Debug Mode

Set environment variable `DUCKDANTIC_DEBUG=1` for verbose logging (if implemented).

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/username/duckdantic.git
cd duckdantic

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy src/duckdantic
```

### Code Standards

- All code must pass tests, linting, and type checking
- Follow existing patterns and conventions
- Add tests for new functionality
- Update documentation for API changes

## License

[Check LICENSE.txt for details]

---

_This document serves as the primary reference for understanding and working with the Duckdantic codebase._
