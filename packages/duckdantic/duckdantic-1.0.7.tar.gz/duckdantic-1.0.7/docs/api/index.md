# API Reference

Complete API documentation for Duckdantic.

## Core Modules

### Core API *(Coming Soon)*
Main functions for trait satisfaction checking and field normalization.

### Models *(Coming Soon)*
Duck API classes and Pydantic integration.

### Traits *(Coming Soon)*
Trait and field specifications.

### Matching *(Coming Soon)*
Functions for checking trait satisfaction and getting detailed feedback.

### Providers *(Coming Soon)*
Field extraction from different object types.

### Adapters *(Coming Soon)*
ABC integration and isinstance/issubclass support.

### Algebra *(Coming Soon)*
Set operations on traits (union, intersect, minus).

## Quick Reference

### Essential Functions

```python
from duckdantic import (
    satisfies,      # Check trait satisfaction
    explain,        # Get detailed feedback
    Duck,           # Create duck types
    TraitSpec,      # Define traits
    FieldSpec,      # Define fields
)
```

### Type Checking

```python
# Basic satisfaction check
satisfies(obj, trait, policy=POLICY_PRAGMATIC)

# Detailed explanation
result = explain(obj, trait, policy)
```

### Duck Types

```python
# Create duck type
UserDuck = Duck(User)

# Check with isinstance
isinstance(data, UserDuck)

# Convert objects
user = UserDuck.convert(data)
```

### Traits

```python
# Define trait
trait = TraitSpec(
    name="MyTrait",
    fields=(
        FieldSpec("field1", str, required=True),
        FieldSpec("field2", int, required=False),
    )
)
```

### Policies

```python
from duckdantic import TypeCompatPolicy, POLICY_PRAGMATIC

# Use default policy
satisfies(obj, trait, POLICY_PRAGMATIC)

# Custom policy
strict = TypeCompatPolicy(
    allow_numeric_widening=False,
    allow_optional_widening=False
)
```

### ABC Integration

```python
from duckdantic import abc_for

# Create ABC from trait
MyABC = abc_for(trait)

# Use with isinstance
isinstance(obj, MyABC)
```

### Method Checking

```python
from duckdantic import MethodSpec, methods_satisfy

methods = [
    MethodSpec("method1", params=[int, str], returns=bool),
    MethodSpec("method2", params=[], returns=None),
]

methods_satisfy(obj, methods)
```

### Set Operations

```python
from duckdantic import union, intersect, minus

# Combine traits
combined = union(trait1, trait2)
overlap = intersect(trait1, trait2)
reduced = minus(trait1, ["field_to_remove"])
```

## Module Organization

```
duckdantic/
├── __init__.py          # Main exports
├── traits.py            # TraitSpec, FieldSpec
├── match.py             # satisfies, explain
├── models.py            # Duck, DuckModel, DuckType
├── policy.py            # TypeCompatPolicy, AliasMode
├── normalize.py         # Field normalization
├── compare.py           # Trait comparison
├── algebra.py           # Set operations
├── cache.py             # Performance optimization
├── adapters/
│   └── abc.py          # ABC integration
├── build/
│   └── methods.py      # Method checking
└── providers/          # Field extraction
    ├── base.py         # Provider protocol
    ├── pydantic_v2.py  # Pydantic support
    ├── dataclass.py    # Dataclass support
    ├── typeddict.py    # TypedDict support
    └── ...             # Other providers
```

## Type Exports

All main types are exported from the top-level module:

```python
from duckdantic import (
    # Specifications
    TraitSpec,
    FieldSpec,
    MethodSpec,
    
    # Duck API
    Duck,
    DuckType,
    DuckModel,
    DuckRootModel,
    
    # Functions
    satisfies,
    explain,
    is_duck_of,
    as_duck,
    
    # ABC Integration
    abc_for,
    duckisinstance,
    duckissubclass,
    
    # Method Checking
    methods_satisfy,
    methods_explain,
    
    # Set Operations
    union,
    intersect,
    minus,
    
    # Comparison
    compare_traits,
    TraitRelation,
    
    # Policies
    TypeCompatPolicy,
    POLICY_PRAGMATIC,
    AliasMode,
    
    # Field Views
    FieldView,
    FieldOrigin,
    FieldAliasSet,
    
    # Utilities
    normalize_fields,
    normalize_fields_cached,
    clear_cache,
    get_cache_stats,
    
    # Registry
    TraitRegistry,
)
```