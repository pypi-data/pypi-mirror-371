"""Duck typing for Pydantic models with ergonomic API.

This module provides a fluent API for duck typing with Pydantic models,
fields, and root models, making structural typing as natural as isinstance.

Examples:
    Basic usage::

        from pydantic import BaseModel
        from duckdantic import Duck

        class User(BaseModel):
            id: int
            email: str

        # Create a duck type from the model
        UserDuck = Duck(User)

        # Now use it naturally
        data = {"id": 1, "email": "user@example.com"}
        assert isinstance(data, UserDuck)
        assert UserDuck.validate(data)

        # Or use the model directly with duck protocol
        assert User.__duck_validates__(data)
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, RootModel
from pydantic.fields import FieldInfo

from duckdantic.adapters.abc import abc_for
from duckdantic.match import satisfies
from duckdantic.normalize import normalize_fields
from duckdantic.policy import POLICY_PRAGMATIC, TypeCompatPolicy
from duckdantic.traits import FieldSpec, TraitSpec

T = TypeVar("T")
M = TypeVar("M", bound=BaseModel)


class DuckType:
    """A duck type that can be used with isinstance and validates structure.

    This class wraps a Pydantic model, field, or trait and provides
    isinstance support through metaclass magic.

    Examples:
        Create from model::

            class Product(BaseModel):
                id: int
                name: str
                price: float

            ProductDuck = Duck(Product)

            # Works with isinstance
            data = {"id": 1, "name": "Widget", "price": 9.99}
            assert isinstance(data, ProductDuck)
    """

    def __init__(
        self,
        source: type[BaseModel] | FieldInfo | TraitSpec,
        *,
        policy: TypeCompatPolicy = POLICY_PRAGMATIC,
        name: str | None = None,
    ):
        """Initialize a duck type.

        Args:
            source: The source to create duck type from (Model, Field, or Trait).
            policy: Type checking policy to use.
            name: Optional name for the duck type.
        """
        self.source = source
        self.policy = policy
        self._trait: TraitSpec | None = None
        self._abc: type | None = None

        # Determine name
        if name:
            self.name = name
        elif isinstance(source, type) and issubclass(source, BaseModel):
            self.name = f"{source.__name__}Duck"
        elif isinstance(source, TraitSpec):
            self.name = f"{source.name}Duck" if source.name else "Duck"
        elif isinstance(source, FieldInfo):
            self.name = "FieldDuck"
        else:
            self.name = "Duck"

    @property
    def trait(self) -> TraitSpec:
        """Get the trait specification for this duck type."""
        if self._trait is None:
            if isinstance(self.source, type) and issubclass(self.source, BaseModel):
                # Convert model to trait
                fields = normalize_fields(self.source)
                # Try to get required info from model
                required_fields = set()
                if hasattr(self.source, "model_fields"):
                    # Pydantic v2
                    for name, field_info in self.source.model_fields.items():
                        if getattr(field_info, "is_required", lambda: True)():
                            required_fields.add(name)

                field_specs = [
                    FieldSpec(
                        name=field.name,
                        typ=field.annotation,
                        required=field.name in required_fields,
                        accept_alias=bool(field.aliases),
                        check_types=True,
                    )
                    for field in fields.values()
                ]
                self._trait = TraitSpec(
                    name=self.source.__name__,
                    fields=field_specs,
                )
            elif isinstance(self.source, TraitSpec):
                self._trait = self.source
            elif isinstance(self.source, FieldInfo):
                # Create trait from single field
                self._trait = TraitSpec(
                    name="Field",
                    fields=[
                        FieldSpec(
                            name="value",
                            typ=self.source.annotation,
                            required=(
                                self.source.is_required()
                                if hasattr(self.source, "is_required")
                                else True
                            ),
                        ),
                    ],
                )
            else:
                raise TypeError(
                    f"Cannot create trait from {type(self.source)}",
                )
        return self._trait

    @property
    def abc(self) -> type:
        """Get the ABC for isinstance checks."""
        if self._abc is None:
            self._abc = abc_for(self.trait, self.policy, name=self.name)
        return self._abc

    def __class_getitem__(cls, params):
        """Support generic syntax like Duck[User]."""
        if not isinstance(params, tuple):
            params = (params,)
        return cls(params[0])

    def __instancecheck__(self, instance: Any) -> bool:
        """Support isinstance(obj, DuckType)."""
        return isinstance(instance, self.abc)

    def __subclasscheck__(self, subclass: Any) -> bool:
        """Support issubclass(cls, DuckType)."""
        return issubclass(subclass, self.abc)

    def validate(self, obj: Any) -> bool:
        """Check if object satisfies this duck type.

        Args:
            obj: Object to validate.

        Returns:
            True if object satisfies the duck type.
        """
        return satisfies(obj, self.trait, self.policy)

    def assert_valid(self, obj: Any, message: str | None = None) -> None:
        """Assert that object satisfies this duck type.

        Args:
            obj: Object to validate.
            message: Optional custom error message.

        Raises:
            TypeError: If object doesn't satisfy duck type.
        """
        if not self.validate(obj):
            msg = message or f"Object does not satisfy {self.name}"
            raise TypeError(msg)

    def convert(self, obj: Any, **kwargs) -> Any:
        """Convert object to the source model type if possible.

        Args:
            obj: Object to convert.
            **kwargs: Additional arguments for model construction.

        Returns:
            Instance of the source model.

        Raises:
            ValueError: If conversion fails.
        """
        if isinstance(self.source, type) and issubclass(self.source, BaseModel):
            return self.source.model_validate(obj, **kwargs)
        raise ValueError(f"Cannot convert to {type(self.source)}")


class DuckMeta(type):
    """Metaclass for Duck that enables isinstance checks."""

    def __instancecheck__(cls, instance):
        if hasattr(instance, "__duck_type__"):
            return isinstance(instance, instance.__duck_type__.abc)
        return False


class Duck(metaclass=DuckMeta):
    """Factory for creating duck types with natural syntax.

    Can be used as:
    - Duck(Model) - Create duck type from model
    - Duck[Model] - Generic syntax
    - isinstance(obj, Duck(Model)) - Direct isinstance usage

    Examples:
        Various ways to create and use duck types::

            from pydantic import BaseModel
            from duckdantic import Duck

            class User(BaseModel):
                id: int
                email: str

            # Create duck type
            UserDuck = Duck(User)

            # Or use generic syntax
            UserDuck = Duck[User]

            # Check with isinstance
            data = {"id": 1, "email": "a@b.com"}
            assert isinstance(data, UserDuck)
            assert isinstance(data, Duck(User))

            # Validate and convert
            if UserDuck.validate(data):
                user = UserDuck.convert(data)
    """

    def __new__(
        cls,
        source: type[BaseModel] | FieldInfo | TraitSpec,
        *,
        policy: TypeCompatPolicy = POLICY_PRAGMATIC,
        name: str | None = None,
    ) -> DuckType:
        """Create a new duck type."""
        return DuckType(source, policy=policy, name=name)

    @classmethod
    def __class_getitem__(cls, params):
        """Support Duck[Model] syntax."""
        if not isinstance(params, tuple):
            params = (params,)
        return DuckType(params[0])


# Monkey-patch BaseModel to add duck typing protocol
def _duck_validates(
    cls: type[BaseModel],
    obj: Any,
    policy: TypeCompatPolicy = POLICY_PRAGMATIC,
) -> bool:
    """Check if object satisfies model structure."""
    duck_type = DuckType(cls, policy=policy)
    return duck_type.validate(obj)


def _duck_convert(cls: type[M], obj: Any, **kwargs) -> M:
    """Convert duck-typed object to model instance."""
    # For dict, merge with kwargs and validate
    if isinstance(obj, dict):
        data = {**obj, **kwargs}
        return cls.model_validate(data)

    # For objects, extract relevant fields
    if not cls.__duck_validates__(obj.__class__ if hasattr(obj, "__class__") else obj):
        raise ValueError(f"Object does not satisfy {cls.__name__} structure")

    # Extract data from object
    data = {}
    if hasattr(obj, "model_dump"):
        # Pydantic model
        data = obj.model_dump()
    elif hasattr(obj, "__dict__"):
        # Regular object
        data = {}
        for field in cls.model_fields:
            if hasattr(obj, field):
                data[field] = getattr(obj, field)
    else:
        # Try to validate directly
        data = obj

    # Merge with kwargs
    data = {**data, **kwargs} if isinstance(data, dict) else data
    return cls.model_validate(data)


# Add duck typing methods to BaseModel
BaseModel.__duck_validates__ = classmethod(_duck_validates)
BaseModel.__duck_convert__ = classmethod(_duck_convert)


# Convenience functions
def is_duck_of(
    obj: Any,
    model: type[BaseModel],
    policy: TypeCompatPolicy = POLICY_PRAGMATIC,
) -> bool:
    """Check if object is duck-type compatible with model.

    Args:
        obj: Object to check.
        model: Pydantic model to check against.
        policy: Type checking policy.

    Returns:
        True if object satisfies model structure.

    Examples:
        Quick duck type checks::

            from duckdantic import is_duck_of

            data = {"id": 1, "email": "user@example.com"}

            if is_duck_of(data, User):
                print("It's user-like!")
    """
    return Duck(model, policy=policy).validate(obj)


def as_duck(model: type[M], obj: Any, **kwargs) -> M:
    """Convert object to model using duck typing.

    Args:
        model: Target Pydantic model.
        obj: Object to convert.
        **kwargs: Additional arguments for model.

    Returns:
        Instance of model.

    Raises:
        ValueError: If object doesn't satisfy model.

    Examples:
        Convert various objects::

            from duckdantic import as_duck

            # From dict
            user = as_duck(User, {"id": 1, "email": "a@b.com"})

            # From another object
            customer = Customer(id=2, email="b@c.com", company="ACME")
            user = as_duck(User, customer)
    """
    return model.__duck_convert__(obj, **kwargs)


class DuckModel(BaseModel):
    """Base model with enhanced duck typing support.

    Provides additional duck typing methods and properties.

    Examples:
        Enhanced model::

            class User(DuckModel):
                id: int
                email: str

            # Get duck type
            UserDuck = User.duck_type

            # Use as ABC
            data = {"id": 1, "email": "a@b.com"}
            assert isinstance(data, User.duck_type)
    """

    @classmethod
    def duck_type(cls) -> DuckType:
        """Get the duck type for this model."""
        if not hasattr(cls, "_duck_type"):
            cls._duck_type = Duck(cls)
        return cls._duck_type

    @classmethod
    def is_duck(cls, obj: Any, policy: TypeCompatPolicy = POLICY_PRAGMATIC) -> bool:
        """Check if object is duck-type compatible."""
        return cls.__duck_validates__(obj, policy)

    @classmethod
    def from_duck(cls: type[M], obj: Any, **kwargs) -> M:
        """Create instance from duck-typed object."""
        return cls.__duck_convert__(obj, **kwargs)


class DuckRootModel(RootModel[T], Generic[T]):
    """Root model with duck typing support.

    Examples:
        List of users::

            class UserList(DuckRootModel[List[User]]):
                pass

            data = [
                {"id": 1, "email": "a@b.com"},
                {"id": 2, "email": "c@d.com"}
            ]

            assert UserList.__duck_validates__(data)
            users = UserList.from_duck(data)
    """

    @classmethod
    def __duck_validates__(
        cls,
        obj: Any,
        policy: TypeCompatPolicy = POLICY_PRAGMATIC,
    ) -> bool:
        """Check if object satisfies root model structure."""
        try:
            cls.model_validate(obj)
            return True
        except Exception:
            return False

    @classmethod
    def from_duck(cls: type[M], obj: Any, **kwargs) -> M:
        """Create instance from duck-typed object."""
        return cls.model_validate(obj, **kwargs)
