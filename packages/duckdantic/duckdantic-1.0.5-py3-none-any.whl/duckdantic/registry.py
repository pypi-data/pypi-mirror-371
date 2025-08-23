"""In-memory trait registry for duckdantic."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from duckdantic.match import satisfies
from duckdantic.policy import TypeCompatPolicy
from duckdantic.traits import TraitSpec


@dataclass
class TraitRegistry:
    """Simple registry with compatibility queries."""

    _traits: dict[str, TraitSpec] = field(default_factory=dict)

    def add(self, trait: TraitSpec) -> None:
        """Add or replace a trait by name."""
        self._traits[trait.name] = trait

    def get(self, name: str) -> TraitSpec | None:
        """Retrieve a trait by name."""
        return self._traits.get(name)

    def list(self) -> Iterable[TraitSpec]:
        """Iterate all registered traits."""
        return self._traits.values()

    def find_compatible(
        self,
        obj: object,
        policy: TypeCompatPolicy,
    ) -> Mapping[str, bool]:
        """Return a map of trait name -> satisfied?

        for the given object.
        """
        return {name: satisfies(obj, tr, policy) for name, tr in self._traits.items()}
