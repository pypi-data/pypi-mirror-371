"""Abstract Base Class adapter for duckdantic traits.

This module provides tools to create runtime ABCs that delegate their
subclass checks to duckdantic's structural type checking. This allows
traits to integrate seamlessly with Python's isinstance() and issubclass()
built-in functions.

Examples:
    Create an ABC from a trait::

        from duckdantic import TraitSpec, FieldSpec
        from duckdantic.adapters import abc_for

        user_trait = TraitSpec(
            name="User",
            fields=[
                FieldSpec(name="id", type=int, required=True),
                FieldSpec(name="email", type=str, required=True),
            ]
        )

        UserABC = abc_for(user_trait)

        # Now works with isinstance
        assert isinstance(user_obj, UserABC)

    Direct duck-typing checks::

        from duckdantic.adapters import duckisinstance, duckissubclass

        # Check instances
        if duckisinstance(obj, user_trait):
            print("Object satisfies User trait")

        # Check classes
        if duckissubclass(MyClass, user_trait):
            print("MyClass satisfies User trait")
"""

from __future__ import annotations

from abc import ABCMeta
from dataclasses import replace
from typing import Any

from duckdantic.match import satisfies
from duckdantic.policy import POLICY_PRAGMATIC, TypeCompatPolicy
from duckdantic.traits import TraitSpec

_ABC_CACHE: dict[tuple[int, TypeCompatPolicy], type] = {}


def abc_for(
    trait: TraitSpec,
    policy: TypeCompatPolicy = POLICY_PRAGMATIC,
    *,
    name: str | None = None,
) -> type:
    """Create a runtime ABC whose subclass checks delegate to `satisfies`.

    This function creates an Abstract Base Class that uses duckdantic's
    structural type checking for its __subclasshook__. This allows traits
    to work with Python's built-in isinstance() and issubclass() functions.

    The created ABCs are cached based on trait identity and policy to avoid
    recreating identical classes.

    Args:
        trait: The trait specification to convert to an ABC.
        policy: Type compatibility policy to use for checking.
        name: Optional name for the generated ABC class. If not provided,
            defaults to "{trait.name}ABC" or "TraitABC" if trait has no name.

    Returns:
        A new ABC class that checks structural compatibility using the trait.

    Examples:
        Basic ABC creation::

            from duckdantic import TraitSpec, FieldSpec
            from duckdantic.adapters import abc_for

            person_trait = TraitSpec(
                name="Person",
                fields=[
                    FieldSpec(name="name", type=str, required=True),
                    FieldSpec(name="age", type=int, required=True),
                ]
            )

            PersonABC = abc_for(person_trait)

            class Employee:
                def __init__(self, name: str, age: int, dept: str):
                    self.name = name
                    self.age = age
                    self.dept = dept

            emp = Employee("Alice", 30, "Engineering")
            assert isinstance(emp, PersonABC)  # True!

        With custom name and policy::

            from duckdantic.policy import POLICY_STRICT

            StrictUserABC = abc_for(
                user_trait,
                policy=POLICY_STRICT,
                name="StrictUser"
            )
    """
    policy = replace(policy)
    key = (id(trait), policy)
    cached = _ABC_CACHE.get(key)
    if cached is not None:
        return cached

    abc_name = name or f"{trait.name or 'Trait'}ABC"

    class _TraitABC(metaclass=ABCMeta):
        pass

    _TraitABC.__name__ = abc_name

    @classmethod
    def __subclasshook__(cls, candidate: Any):
        try:
            return bool(satisfies(candidate, trait, policy))
        except Exception:
            return NotImplemented

    _TraitABC.__subclasshook__ = __subclasshook__  # type: ignore[attr-defined]
    _ABC_CACHE[key] = _TraitABC
    return _TraitABC


def duckissubclass(
    candidate: Any,
    trait: TraitSpec,
    policy: TypeCompatPolicy = POLICY_PRAGMATIC,
) -> bool:
    """Check if a class satisfies a trait specification.

    This is a convenience function that directly checks if a class
    satisfies a trait without creating an intermediate ABC.

    Args:
        candidate: The class to check.
        trait: The trait specification to check against.
        policy: Type compatibility policy to use.

    Returns:
        True if the class satisfies the trait, False otherwise.

    Examples:
        Check class compatibility::

            from duckdantic.adapters import duckissubclass

            class Product:
                id: int
                name: str
                price: float

            if duckissubclass(Product, product_trait):
                print("Product class matches the trait")
    """
    return bool(satisfies(candidate, trait, policy))


def duckisinstance(
    obj: Any,
    trait: TraitSpec,
    policy: TypeCompatPolicy = POLICY_PRAGMATIC,
) -> bool:
    """Check if an instance satisfies a trait specification.

    This is a convenience function that directly checks if an object
    satisfies a trait without creating an intermediate ABC.

    Args:
        obj: The object instance to check.
        trait: The trait specification to check against.
        policy: Type compatibility policy to use.

    Returns:
        True if the object satisfies the trait, False otherwise.

    Examples:
        Check instance compatibility::

            from duckdantic.adapters import duckisinstance

            user_data = {"id": 123, "email": "user@example.com"}

            if duckisinstance(user_data, user_trait):
                print("Data satisfies user trait")
    """
    return bool(satisfies(obj, trait, policy))
