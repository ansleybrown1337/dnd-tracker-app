"""Application use cases for Phase 1."""

from __future__ import annotations

from .catalog import ReferenceCatalog
from .database import SQLiteRepository
from .domain import (
    Campaign,
    Character,
    InventoryEntry,
    InventoryInstance,
    ItemDefinition,
    ValidationError,
    optional_text,
    required_text,
    validate_character,
    validate_custom_item,
)


class NotFoundError(LookupError):
    """Raised when a requested persisted or catalog object does not exist."""


class CharacterManagerService:
    def __init__(self, repository: SQLiteRepository, catalog: ReferenceCatalog) -> None:
        self.repository = repository
        self.catalog = catalog

    def initialize(self) -> None:
        self.repository.initialize()

    def list_campaigns(self) -> list[Campaign]:
        return self.repository.list_campaigns()

    def create_campaign(self, name: str) -> Campaign:
        return self.repository.create_campaign(required_text(name, "Campaign name"))

    def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self.repository.get_campaign(campaign_id)
        if campaign is None:
            raise NotFoundError("Campaign not found.")
        return campaign

    def list_characters(self, campaign_id: str) -> list[Character]:
        self.get_campaign(campaign_id)
        return self.repository.list_characters(campaign_id)

    def create_character(
        self,
        *,
        campaign_id: str,
        name: str,
        level: int,
        class_name: str,
        species_name: str,
        current_hp: int,
        maximum_hp: int,
        notes: str = "",
    ) -> Character:
        self.get_campaign(campaign_id)
        values = validate_character(
            name=name,
            level=level,
            class_name=class_name,
            species_name=species_name,
            current_hp=current_hp,
            maximum_hp=maximum_hp,
            notes=notes,
        )
        return self.repository.create_character(
            campaign_id=campaign_id,
            name=values[0],
            level=values[1],
            class_name=values[2],
            species_name=values[3],
            current_hp=values[4],
            maximum_hp=values[5],
            notes=values[6],
        )

    def get_character(self, character_id: str) -> Character:
        character = self.repository.get_character(character_id)
        if character is None:
            raise NotFoundError("Character not found.")
        return character

    def update_character(
        self,
        *,
        character_id: str,
        name: str,
        level: int,
        class_name: str,
        species_name: str,
        current_hp: int,
        maximum_hp: int,
        notes: str,
    ) -> Character:
        self.get_character(character_id)
        values = validate_character(
            name=name,
            level=level,
            class_name=class_name,
            species_name=species_name,
            current_hp=current_hp,
            maximum_hp=maximum_hp,
            notes=notes,
        )
        character = self.repository.update_character(
            character_id=character_id,
            name=values[0],
            level=values[1],
            class_name=values[2],
            species_name=values[3],
            current_hp=values[4],
            maximum_hp=values[5],
            notes=values[6],
        )
        if character is None:  # pragma: no cover - guarded above
            raise NotFoundError("Character not found.")
        return character

    def search_catalog(self, query: str = "") -> list[ItemDefinition]:
        return self.catalog.search(query)

    def get_item_definition(self, definition_id: str) -> ItemDefinition:
        item = self.catalog.get(definition_id)
        if item is None:
            raise NotFoundError("Item definition not found.")
        return item

    def create_custom_item(
        self,
        *,
        name: str,
        category: str,
        damage: str = "",
        damage_type: str = "",
        properties: tuple[str, ...] = (),
        mastery: str = "",
        weight: float | None = None,
        cost_quantity: int | None = None,
        cost_unit: str = "",
        description: str = "",
    ) -> ItemDefinition:
        values = validate_custom_item(
            name=name,
            category=category,
            damage=damage,
            damage_type=damage_type,
            properties=properties,
            mastery=mastery,
            weight=weight,
            cost_quantity=cost_quantity,
            cost_unit=cost_unit,
            description=description,
        )
        return self.repository.create_custom_item(
            name=values[0],
            category=values[1],
            damage=values[2],
            damage_type=values[3],
            properties=values[4],
            mastery=values[5],
            weight=values[6],
            cost_quantity=values[7],
            cost_unit=values[8],
            description=values[9],
        )

    def list_inventory(self, character_id: str) -> list[InventoryEntry]:
        self.get_character(character_id)
        entries = []
        for instance in self.repository.list_inventory(character_id):
            definition = self.catalog.get(instance.definition_id)
            if definition is None:
                raise NotFoundError(
                    f"Inventory definition {instance.definition_id!r} is unavailable."
                )
            entries.append(InventoryEntry(instance, definition))
        return entries

    def add_inventory(
        self,
        *,
        character_id: str,
        definition_id: str,
        quantity: int = 1,
        notes: str = "",
    ) -> InventoryInstance:
        self.get_character(character_id)
        self.get_item_definition(definition_id)
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1.")
        clean_notes = optional_text(notes, "Inventory notes", maximum=2_000)
        return self.repository.add_inventory(
            character_id=character_id,
            definition_id=definition_id,
            quantity=quantity,
            notes=clean_notes,
        )

    def update_inventory(self, *, instance_id: str, quantity: int, notes: str) -> InventoryInstance:
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1.")
        clean_notes = optional_text(notes, "Inventory notes", maximum=2_000)
        instance = self.repository.update_inventory(
            instance_id=instance_id, quantity=quantity, notes=clean_notes
        )
        if instance is None:
            raise NotFoundError("Inventory item not found.")
        return instance

    def remove_inventory(self, instance_id: str) -> None:
        if not self.repository.remove_inventory(instance_id):
            raise NotFoundError("Inventory item not found.")
