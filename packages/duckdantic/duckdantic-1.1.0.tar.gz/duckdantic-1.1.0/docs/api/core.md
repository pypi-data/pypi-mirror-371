# Core API

Core functions for trait satisfaction checking and field normalization.

## Functions

### satisfies

Check if an object satisfies a trait specification.

```python
def satisfies(
    obj: Any,
    trait: TraitSpec,
    policy: TypeCompatPolicy = POLICY_PRAGMATIC
) -> bool
```

**Parameters:**
- `obj`: The object to check (class, instance, or mapping)
- `trait`: The trait specification to check against
- `policy`: Type compatibility policy (default: POLICY_PRAGMATIC)

**Returns:**
- `bool`: True if object satisfies the trait

**Example:**
```python
from duckdantic import satisfies, TraitSpec, FieldSpec

user_trait = TraitSpec(
    name="User",
    fields=(
        FieldSpec("id", int, required=True),
        FieldSpec("name", str, required=True),
    )
)

data = {"id": 1, "name": "Alice"}
assert satisfies(data, user_trait)
```

### explain

Get detailed explanation of why an object does or doesn't satisfy a trait.

```python
def explain(
    obj: Any,
    trait: TraitSpec,
    policy: TypeCompatPolicy = POLICY_PRAGMATIC
) -> dict
```

**Parameters:**
- `obj`: The object to check
- `trait`: The trait specification to check against
- `policy`: Type compatibility policy

**Returns:**
Dictionary containing:
- `ok` (bool): Whether object satisfies trait
- `reasons` (list[str]): Human-readable explanations
- `missing` (list[str]): Missing required fields
- `type_conflicts` (list[dict]): Type mismatch details
- `evidence` (dict): Field-by-field analysis
- `alias_considered` (dict): Aliases that were checked

**Example:**
```python
from duckdantic import explain

result = explain({"id": "not-a-number"}, user_trait)
print(result)
# {
#     'ok': False,
#     'reasons': ["type mismatch for 'id'", "missing required field 'name'"],
#     'missing': ['name'],
#     'type_conflicts': [{
#         'name': 'id',
#         'actual': 'str',
#         'desired': 'int',
#         'why': {...}
#     }],
#     ...
# }
```

### normalize_fields

Extract and normalize fields from various object types.

```python
def normalize_fields(obj: Any) -> dict[str, FieldView]
```

**Parameters:**
- `obj`: Object to extract fields from

**Returns:**
- Dictionary mapping field names to FieldView objects

**Supported Types:**
- Pydantic models (v2)
- Dataclasses
- TypedDict
- attrs classes
- Plain classes with annotations
- Dictionaries
- Instances (delegates to class)

**Example:**
```python
from duckdantic import normalize_fields
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

fields = normalize_fields(User)
for name, field in fields.items():
    print(f"{name}: {field.annotation}")
# id: <class 'int'>
# name: <class 'str'>
```

### normalize_fields_cached

Same as `normalize_fields` but with caching for performance.

```python
def normalize_fields_cached(obj: Any) -> dict[str, FieldView]
```

The cache is keyed by object "shape" for efficient memoization.

## Type Compatibility

### TypeCompatPolicy

Controls how types are compared during satisfaction checks.

```python
@dataclass
class TypeCompatPolicy:
    allow_optional_widening: bool = True
    allow_numeric_widening: bool = True
    desired_union: UnionBranchMode = UnionBranchMode.ANY
    actual_union: UnionBranchMode = UnionBranchMode.ANY
    container_origin_mode: ContainerOriginMode = ContainerOriginMode.RELAXED_PROTOCOL
    annotated_handling: AnnotatedHandling = AnnotatedHandling.STRIP
    literal_mode: LiteralMode = LiteralMode.COERCE_TO_BASE
    alias_mode: AliasMode = AliasMode.USE_BOTH
```

### POLICY_PRAGMATIC

Default policy with sensible defaults:
- Allows numeric widening (int → float)
- Allows optional widening (T → Optional[T])
- Relaxed container checking
- Supports aliases

```python
from duckdantic import POLICY_PRAGMATIC

# Use default policy
satisfies(obj, trait, POLICY_PRAGMATIC)
```

## Field Information

### FieldView

Information about a single field.

```python
@dataclass
class FieldView:
    name: str                    # Field name
    annotation: Any             # Type annotation
    alias: str | None = None    # Primary alias
    origin: FieldOrigin = ...   # Where field came from
    aliases: FieldAliasSet | None = None  # All aliases
```

### FieldOrigin

Enum indicating where a field was extracted from:

```python
class FieldOrigin(Enum):
    PYDANTIC = "pydantic"
    ANNOTATION = "annotation"  
    ATTRS = "attrs"
    ADHOC = "adhoc"
```

### FieldAliasSet

Collection of field aliases:

```python
@dataclass
class FieldAliasSet:
    primary: str | None = None
    validation: tuple[str, ...] = ()
    serialization: tuple[str, ...] = ()
```

## Cache Management

### clear_cache

Clear the normalization cache.

```python
def clear_cache() -> None
```

### get_cache_stats

Get cache performance statistics.

```python
def get_cache_stats() -> dict
```

**Returns:**
Dictionary with:
- `hits`: Number of cache hits
- `misses`: Number of cache misses
- `size`: Current cache size

**Example:**
```python
from duckdantic import get_cache_stats, clear_cache

stats = get_cache_stats()
print(f"Cache hit rate: {stats['hits'] / (stats['hits'] + stats['misses']):.2%}")

# Clear if needed
clear_cache()
```

## Performance Tips

1. **Use cached normalization**: The cached version is used by default in `satisfies()` and `explain()`

2. **Reuse traits**: Create traits once and reuse them
   ```python
   # Good
   USER_TRAIT = TraitSpec(...)
   
   for data in users:
       if satisfies(data, USER_TRAIT):
           ...
   ```

3. **Batch similar checks**: The cache works best with similar objects
   ```python
   # Check many dicts with same keys
   results = [satisfies(d, trait) for d in similar_dicts]
   ```