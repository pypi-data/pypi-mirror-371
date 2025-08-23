# User Guide

Welcome to the Duckdantic user guide! This guide covers all features in detail.

## Guide Contents

### [Basic Usage](basic-usage.md)

Learn the fundamentals of defining traits, checking satisfaction, and working with different object types.

### [Duck API](duck-api.md)

Master the ergonomic Duck API for seamless integration with Pydantic and natural isinstance usage.

### [Traits](traits.md)

Deep dive into trait specifications, field types, and trait composition.

### [Type Policies](policies.md)

Understand and customize type checking behavior with flexible policies.

### Providers _(Coming Soon)_

Learn how Duckdantic normalizes fields from different object types.

### Advanced Topics _(Coming Soon)_

Explore advanced features like custom matchers, performance optimization, and integration patterns.

## Quick Navigation

<div class="grid cards" markdown>

- :material-play-circle: **New to Duckdantic?**

  ***

  Start with [Basic Usage](basic-usage.md) to learn the fundamentals

- :material-duck: **Using Pydantic?**

  ***

  Jump to the [Duck API](duck-api.md) for the best experience

- :material-cog: **Need Customization?**

  ***

  Check out [Type Policies](policies.md) for fine-tuning validation

- :material-rocket: **Performance Critical?**

  ***

  Advanced optimization strategies coming soon

</div>

## Common Tasks

### Define a Simple Trait

```python
from duckdantic import TraitSpec, FieldSpec

UserTrait = TraitSpec(
    name="User",
    fields=(
        FieldSpec("id", int, required=True),
        FieldSpec("name", str, required=True),
        FieldSpec("email", str, required=False),
    )
)
```

### Check Object Satisfaction

```python
from duckdantic import satisfies

user_data = {"id": 1, "name": "Alice"}
if satisfies(user_data, UserTrait):
    print("Valid user!")
```

### Use Duck Types

```python
from pydantic import BaseModel
from duckdantic import Duck

class User(BaseModel):
    id: int
    name: str

UserDuck = Duck(User)

# Natural isinstance usage
data = {"id": 2, "name": "Bob"}
assert isinstance(data, UserDuck)
```

### Compose Traits

```python
from duckdantic import union, intersect

# Accept either User or Guest
FlexibleTrait = union(UserTrait, GuestTrait)

# Require both User and Admin fields
AdminUserTrait = intersect(UserTrait, AdminTrait)
```

## Best Practices

1. **Start Simple**: Begin with basic traits and add complexity as needed
2. **Reuse Traits**: Define traits once and reuse them across your application
3. **Use Duck API**: When working with Pydantic, prefer the Duck API
4. **Cache Benefits**: Let the built-in cache optimize performance
5. **Clear Names**: Give traits descriptive names for better debugging

## Getting Help

- Check the [API Reference](../api/index.md) for detailed documentation
- Browse [Examples](../examples/index.md) for real-world patterns
- Visit our [GitHub Discussions](https://github.com/pr1m8/duckdantic/discussions) for questions
- Report issues on our [Issue Tracker](https://github.com/pr1m8/duckdantic/issues)
