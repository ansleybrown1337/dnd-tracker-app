"""Core Phase 1 domain types and validation."""

from __future__ import annotations

from dataclasses import dataclass


class ValidationError(ValueError):
    """Raised when user-provided data violates a domain constraint."""


def required_text(value: str, field: str, *, maximum: int = 120) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValidationError(f"{field} is required.")
    if len(cleaned) > maximum:
        raise ValidationError(f"{field} must be {maximum} characters or fewer.")
    return cleaned


def optional_text(value: str, field: str, *, maximum: int) -> str:
    cleaned = value.strip()
    if len(cleaned) > maximum:
        raise ValidationError(f"{field} must be {maximum} characters or fewer.")
    return cleaned


@dataclass(frozen=True, slots=True)
class Campaign:
    id: str
    name: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class Character:
    id: str
    campaign_id: str
    name: str
    level: int
    class_name: str
    species_name: str
    current_hp: int
    maximum_hp: int
    notes: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class ItemDefinition:
    id: str
    source_kind: str
    name: str
    category: str
    damage: str
    damage_type: str
    properties: tuple[str, ...]
    mastery: str
    weight: float | None
    cost_quantity: int | None
    cost_unit: str
    description: str
    source_reference: str

    @property
    def cost_label(self) -> str:
        if self.cost_quantity is None or not self.cost_unit:
            return "—"
        return f"{self.cost_quantity} {self.cost_unit.upper()}"

    @property
    def weight_label(self) -> str:
        if self.weight is None:
            return "—"
        return f"{self.weight:g} lb."


@dataclass(frozen=True, slots=True)
class InventoryInstance:
    id: str
    character_id: str
    definition_id: str
    quantity: int
    notes: str
    created_at: str
    updated_at: str


@dataclass(frozen=True, slots=True)
class InventoryEntry:
    instance: InventoryInstance
    definition: ItemDefinition


def validate_character(
    *,
    name: str,
    level: int,
    class_name: str,
    species_name: str,
    current_hp: int,
    maximum_hp: int,
    notes: str,
) -> tuple[str, int, str, str, int, int, str]:
    clean_name = required_text(name, "Character name")
    if not 1 <= level <= 20:
        raise ValidationError("Level must be between 1 and 20.")
    clean_class = optional_text(class_name, "Class name", maximum=120)
    clean_species = optional_text(species_name, "Species name", maximum=120)
    if maximum_hp < 1:
        raise ValidationError("Maximum HP must be at least 1.")
    if not 0 <= current_hp <= maximum_hp:
        raise ValidationError("Current HP must be between 0 and maximum HP.")
    clean_notes = optional_text(notes, "Notes", maximum=10_000)
    return (
        clean_name,
        level,
        clean_class,
        clean_species,
        current_hp,
        maximum_hp,
        clean_notes,
    )


def validate_custom_item(
    *,
    name: str,
    category: str,
    damage: str,
    damage_type: str,
    properties: tuple[str, ...],
    mastery: str,
    weight: float | None,
    cost_quantity: int | None,
    cost_unit: str,
    description: str,
) -> tuple[str, str, str, str, tuple[str, ...], str, float | None, int | None, str, str]:
    clean_name = required_text(name, "Item name")
    clean_category = required_text(category, "Category")
    clean_damage = optional_text(damage, "Damage", maximum=40)
    clean_damage_type = optional_text(damage_type, "Damage type", maximum=40)
    clean_properties = tuple(
        text for value in properties if (text := optional_text(value, "Property", maximum=80))
    )
    clean_mastery = optional_text(mastery, "Mastery", maximum=40)
    if weight is not None and weight < 0:
        raise ValidationError("Weight cannot be negative.")
    if cost_quantity is not None and cost_quantity < 0:
        raise ValidationError("Cost cannot be negative.")
    clean_cost_unit = optional_text(cost_unit, "Cost unit", maximum=10).lower()
    if cost_quantity is not None and not clean_cost_unit:
        raise ValidationError("Cost unit is required when a cost is provided.")
    clean_description = optional_text(description, "Description", maximum=4_000)
    return (
        clean_name,
        clean_category,
        clean_damage,
        clean_damage_type,
        clean_properties,
        clean_mastery,
        weight,
        cost_quantity,
        clean_cost_unit,
        clean_description,
    )
