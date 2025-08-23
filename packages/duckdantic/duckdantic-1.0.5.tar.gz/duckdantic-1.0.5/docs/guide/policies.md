# Type Policies

Type policies control how Duckdantic compares types during satisfaction checks. This guide covers all policy options and common customization patterns.

## Overview

A `TypeCompatPolicy` defines rules for type compatibility:

```python
from duckdantic import TypeCompatPolicy, satisfies

# Use custom policy
policy = TypeCompatPolicy(
    allow_numeric_widening=False,  # Strict numeric types
    allow_optional_widening=True,   # T can satisfy Optional[T]
)

satisfies(obj, trait, policy)
```

## Default Policy

The default `POLICY_PRAGMATIC` provides sensible defaults:

```python
from duckdantic import POLICY_PRAGMATIC

# Default settings
POLICY_PRAGMATIC = TypeCompatPolicy(
    allow_optional_widening=True,
    allow_numeric_widening=True,
    desired_union=UnionBranchMode.ANY,
    actual_union=UnionBranchMode.ANY,
    container_origin_mode=ContainerOriginMode.RELAXED_PROTOCOL,
    annotated_handling=AnnotatedHandling.STRIP,
    literal_mode=LiteralMode.COERCE_TO_BASE,
    alias_mode=AliasMode.USE_BOTH,
)
```

## Policy Options

### allow_numeric_widening

Controls whether numeric types can widen (int → float, float → complex):

```python
from duckdantic import TraitSpec, FieldSpec, satisfies, TypeCompatPolicy

PriceTrait = TraitSpec(
    name="Price",
    fields=(FieldSpec("amount", float, required=True),)
)

# With numeric widening (default)
assert satisfies({"amount": 100}, PriceTrait)  # int → float OK

# Without numeric widening
strict = TypeCompatPolicy(allow_numeric_widening=False)
assert not satisfies({"amount": 100}, PriceTrait, strict)  # int ≠ float
```

### allow_optional_widening

Controls whether T can satisfy Optional[T]:

```python
OptionalEmailTrait = TraitSpec(
    name="OptionalEmail",
    fields=(FieldSpec("email", Optional[str], required=True),)
)

# With optional widening (default)
assert satisfies({"email": "user@example.com"}, OptionalEmailTrait)  # str → Optional[str] OK

# Without optional widening
strict = TypeCompatPolicy(allow_optional_widening=False)
assert not satisfies({"email": "user@example.com"}, OptionalEmailTrait, strict)
```

### Union Handling

Control how Union types are matched:

```python
from typing import Union

# UnionBranchMode options:
# - ANY: Match if any branch matches
# - ALL: Must match all branches

FlexibleIdTrait = TraitSpec(
    name="FlexibleId",
    fields=(FieldSpec("id", Union[int, str], required=True),)
)

# ANY mode (default) - either int or str works
assert satisfies({"id": 123}, FlexibleIdTrait)
assert satisfies({"id": "ABC"}, FlexibleIdTrait)
```

### Container Origin Mode

Controls how strictly container types are checked:

```python
from typing import List, Sequence

# ContainerOriginMode options:
# - STRICT: Exact origin match (list ≠ List)
# - RELAXED: Accept runtime/typing equivalents
# - RELAXED_PROTOCOL: Also accept compatible protocols

SequenceTrait = TraitSpec(
    name="Sequence",
    fields=(FieldSpec("items", Sequence[int], required=True),)
)

# RELAXED_PROTOCOL mode (default) - list satisfies Sequence
assert satisfies({"items": [1, 2, 3]}, SequenceTrait)

# STRICT mode
strict = TypeCompatPolicy(container_origin_mode=ContainerOriginMode.STRICT)
# Would require exact Sequence type
```

### Literal Mode

Control how Literal types are handled:

```python
from typing import Literal

StatusTrait = TraitSpec(
    name="Status",
    fields=(FieldSpec("status", Literal["active", "inactive"], required=True),)
)

# LiteralMode options:
# - EXACT_MATCH: Value must be in literal values
# - COERCE_TO_BASE: Also accept base type (str)
# - COERCE_VALUES_TO_BASE: Compare as base types

# COERCE_TO_BASE (default) - accepts literal values only
assert satisfies({"status": "active"}, StatusTrait)
assert not satisfies({"status": "pending"}, StatusTrait)
```

### Alias Mode

Control which aliases are considered:

```python
from duckdantic import AliasMode

# AliasMode options:
# - DISALLOW: No aliases
# - ALLOW_PRIMARY: Only primary alias
# - USE_VALIDATION: Validation aliases
# - USE_SERIALIZATION: Serialization aliases
# - USE_BOTH: All aliases (default)

policy = TypeCompatPolicy(alias_mode=AliasMode.ALLOW_PRIMARY)
```

## Common Policy Patterns

### Strict Type Checking

For maximum type safety:

```python
STRICT_POLICY = TypeCompatPolicy(
    allow_optional_widening=False,
    allow_numeric_widening=False,
    container_origin_mode=ContainerOriginMode.STRICT,
    literal_mode=LiteralMode.EXACT_MATCH,
    alias_mode=AliasMode.DISALLOW,
)

# Use for critical validation
if not satisfies(data, trait, STRICT_POLICY):
    raise TypeError("Exact type match required")
```

### Lenient Validation

For maximum flexibility:

```python
LENIENT_POLICY = TypeCompatPolicy(
    allow_optional_widening=True,
    allow_numeric_widening=True,
    container_origin_mode=ContainerOriginMode.RELAXED_PROTOCOL,
    literal_mode=LiteralMode.COERCE_VALUES_TO_BASE,
    alias_mode=AliasMode.USE_BOTH,
)

# Use for data migration or loose validation
if satisfies(legacy_data, trait, LENIENT_POLICY):
    # Attempt conversion
    pass
```

### API Validation

For validating external API data:

```python
API_POLICY = TypeCompatPolicy(
    allow_optional_widening=True,    # APIs might omit None
    allow_numeric_widening=True,      # JSON numbers are tricky
    container_origin_mode=ContainerOriginMode.RELAXED,
    alias_mode=AliasMode.USE_VALIDATION,  # Check input aliases
)

def validate_api_response(data: dict, expected_trait: TraitSpec):
    if not satisfies(data, expected_trait, API_POLICY):
        result = explain(data, expected_trait, API_POLICY)
        raise ValueError(f"Invalid API response: {result['reasons']}")
```

### Internal Validation

For internal type checking:

```python
INTERNAL_POLICY = TypeCompatPolicy(
    allow_optional_widening=False,   # Be explicit about None
    allow_numeric_widening=False,    # Be explicit about types
    container_origin_mode=ContainerOriginMode.RELAXED,
    alias_mode=AliasMode.DISALLOW,   # Use real field names
)

# Use within application boundaries
def process_internal_data(data: dict):
    assert satisfies(data, InternalTrait, INTERNAL_POLICY)
```

## Policy Composition

Create specialized policies by modifying defaults:

```python
from dataclasses import replace

# Start with default
base_policy = POLICY_PRAGMATIC

# Create variations
strict_numbers = replace(base_policy, allow_numeric_widening=False)
no_aliases = replace(base_policy, alias_mode=AliasMode.DISALLOW)
exact_types = replace(
    base_policy,
    allow_optional_widening=False,
    allow_numeric_widening=False,
)
```

## Dynamic Policies

Choose policies based on context:

```python
def get_validation_policy(context: str) -> TypeCompatPolicy:
    """Get appropriate policy for context."""
    policies = {
        "api": API_POLICY,
        "internal": INTERNAL_POLICY,
        "migration": LENIENT_POLICY,
        "strict": STRICT_POLICY,
    }
    return policies.get(context, POLICY_PRAGMATIC)

# Use dynamic policy
def validate_data(data: dict, trait: TraitSpec, context: str):
    policy = get_validation_policy(context)
    return satisfies(data, trait, policy)
```

## Testing with Policies

Test trait satisfaction under different policies:

```python
import pytest
from duckdantic import satisfies, TypeCompatPolicy

def test_trait_with_policies():
    data = {"value": 42}  # int
    float_trait = TraitSpec(
        name="Float",
        fields=(FieldSpec("value", float),)
    )

    # Should pass with default policy
    assert satisfies(data, float_trait)

    # Should fail with strict policy
    strict = TypeCompatPolicy(allow_numeric_widening=False)
    assert not satisfies(data, float_trait, strict)
```

## Performance Considerations

Policies don't affect caching - the same normalized fields are used:

```python
# These all use the same cached normalization
satisfies(obj, trait, POLICY_PRAGMATIC)
satisfies(obj, trait, STRICT_POLICY)
satisfies(obj, trait, LENIENT_POLICY)
```

## Best Practices

1. **Use defaults when possible**: `POLICY_PRAGMATIC` works for most cases
2. **Document policy choices**: Explain why you're using a custom policy
3. **Test with multiple policies**: Ensure your code works as expected
4. **Create named policies**: Define policies as constants for reuse
5. **Consider the context**: APIs, migrations, and internal code have different needs

## Common Pitfalls

### Over-Strictness

```python
# Too strict for JSON data
strict = TypeCompatPolicy(
    allow_numeric_widening=False,  # JSON doesn't distinguish int/float
    container_origin_mode=ContainerOriginMode.STRICT,  # JSON uses plain lists
)

# Better for JSON
json_friendly = TypeCompatPolicy(
    allow_numeric_widening=True,
    container_origin_mode=ContainerOriginMode.RELAXED,
)
```

### Alias Confusion

```python
# If using Pydantic with aliases, don't disable them
bad_policy = TypeCompatPolicy(alias_mode=AliasMode.DISALLOW)

# This will fail even though the data is valid
pydantic_model = Model(id=1)  # Uses alias
trait = TraitSpec(fields=(FieldSpec("user_id", int),))
satisfies(pydantic_model, trait, bad_policy)  # False!
```

## Next Steps

- Explore Providers (coming soon) to understand field extraction
- Read Advanced Topics (coming soon) for complex scenarios
- Check [Examples](../examples/index.md) for real-world usage
