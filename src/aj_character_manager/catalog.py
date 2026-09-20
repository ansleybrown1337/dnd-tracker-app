"""Reference catalog abstraction and the reviewed Phase 1 fixture."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from .domain import ItemDefinition

SRD_SOURCE = "SRD 5.2.1, Weapons table, page 91"


def _weapon(
    slug: str,
    name: str,
    category: str,
    damage: str,
    damage_type: str,
    properties: tuple[str, ...],
    mastery: str,
    weight: float,
    cost_quantity: int,
    cost_unit: str,
) -> ItemDefinition:
    return ItemDefinition(
        id=f"srd-5.2.1:weapon:{slug}",
        source_kind="bundled",
        name=name,
        category=category,
        damage=damage,
        damage_type=damage_type,
        properties=properties,
        mastery=mastery,
        weight=weight,
        cost_quantity=cost_quantity,
        cost_unit=cost_unit,
        description="A reviewed Phase 1 weapon definition from SRD 5.2.1.",
        source_reference=SRD_SOURCE,
    )


BUILTIN_ITEMS: tuple[ItemDefinition, ...] = (
    _weapon(
        "club", "Club", "Simple Melee Weapon", "1d4", "Bludgeoning", ("Light",), "Slow", 2, 1, "sp"
    ),
    _weapon(
        "dagger",
        "Dagger",
        "Simple Melee Weapon",
        "1d4",
        "Piercing",
        ("Finesse", "Light", "Thrown (20/60)"),
        "Nick",
        1,
        2,
        "gp",
    ),
    _weapon(
        "greatclub",
        "Greatclub",
        "Simple Melee Weapon",
        "1d8",
        "Bludgeoning",
        ("Two-Handed",),
        "Push",
        10,
        2,
        "sp",
    ),
    _weapon(
        "handaxe",
        "Handaxe",
        "Simple Melee Weapon",
        "1d6",
        "Slashing",
        ("Light", "Thrown (20/60)"),
        "Vex",
        2,
        5,
        "gp",
    ),
    _weapon(
        "javelin",
        "Javelin",
        "Simple Melee Weapon",
        "1d6",
        "Piercing",
        ("Thrown (30/120)",),
        "Slow",
        2,
        5,
        "sp",
    ),
    _weapon(
        "light-hammer",
        "Light Hammer",
        "Simple Melee Weapon",
        "1d4",
        "Bludgeoning",
        ("Light", "Thrown (20/60)"),
        "Nick",
        2,
        2,
        "gp",
    ),
    _weapon("mace", "Mace", "Simple Melee Weapon", "1d6", "Bludgeoning", (), "Sap", 4, 5, "gp"),
    _weapon(
        "quarterstaff",
        "Quarterstaff",
        "Simple Melee Weapon",
        "1d6",
        "Bludgeoning",
        ("Versatile (1d8)",),
        "Topple",
        4,
        2,
        "sp",
    ),
    _weapon(
        "spear",
        "Spear",
        "Simple Melee Weapon",
        "1d6",
        "Piercing",
        ("Thrown (20/60)", "Versatile (1d8)"),
        "Sap",
        3,
        1,
        "gp",
    ),
    _weapon(
        "battleaxe",
        "Battleaxe",
        "Martial Melee Weapon",
        "1d8",
        "Slashing",
        ("Versatile (1d10)",),
        "Topple",
        4,
        10,
        "gp",
    ),
    _weapon(
        "longsword",
        "Longsword",
        "Martial Melee Weapon",
        "1d8",
        "Slashing",
        ("Versatile (1d10)",),
        "Sap",
        3,
        15,
        "gp",
    ),
    _weapon(
        "rapier",
        "Rapier",
        "Martial Melee Weapon",
        "1d8",
        "Piercing",
        ("Finesse",),
        "Vex",
        2,
        25,
        "gp",
    ),
    _weapon(
        "shortsword",
        "Shortsword",
        "Martial Melee Weapon",
        "1d6",
        "Piercing",
        ("Finesse", "Light"),
        "Vex",
        2,
        10,
        "gp",
    ),
    _weapon(
        "trident",
        "Trident",
        "Martial Melee Weapon",
        "1d8",
        "Piercing",
        ("Thrown (20/60)", "Versatile (1d10)"),
        "Topple",
        4,
        5,
        "gp",
    ),
    _weapon(
        "warhammer",
        "Warhammer",
        "Martial Melee Weapon",
        "1d8",
        "Bludgeoning",
        ("Versatile (1d10)",),
        "Push",
        5,
        15,
        "gp",
    ),
)


class CustomItemStore(Protocol):
    def list_custom_items(self) -> list[ItemDefinition]: ...

    def get_custom_item(self, definition_id: str) -> ItemDefinition | None: ...


class ReferenceCatalog(Protocol):
    def search(self, query: str = "") -> list[ItemDefinition]: ...

    def get(self, definition_id: str) -> ItemDefinition | None: ...


class ItemCatalog:
    """Combines immutable bundled definitions with persisted custom items."""

    def __init__(
        self,
        custom_store: CustomItemStore,
        bundled_items: Iterable[ItemDefinition] = BUILTIN_ITEMS,
    ) -> None:
        self._custom_store = custom_store
        self._bundled = {item.id: item for item in bundled_items}

    def search(self, query: str = "") -> list[ItemDefinition]:
        needle = query.strip().casefold()
        items = [*self._bundled.values(), *self._custom_store.list_custom_items()]
        if needle:
            items = [item for item in items if needle in self._searchable_text(item)]
        return sorted(items, key=lambda item: (item.name.casefold(), item.id))

    def get(self, definition_id: str) -> ItemDefinition | None:
        return self._bundled.get(definition_id) or self._custom_store.get_custom_item(definition_id)

    @staticmethod
    def _searchable_text(item: ItemDefinition) -> str:
        return " ".join(
            (
                item.name,
                item.category,
                item.damage_type,
                *item.properties,
                item.mastery,
                item.description,
            )
        ).casefold()
