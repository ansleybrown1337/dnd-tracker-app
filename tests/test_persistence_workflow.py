from __future__ import annotations

from pathlib import Path

from aj_character_manager.catalog import ItemCatalog
from aj_character_manager.database import SQLiteRepository
from aj_character_manager.service import CharacterManagerService


def _open_application(database_file: Path) -> CharacterManagerService:
    repository = SQLiteRepository(database_file)
    service = CharacterManagerService(repository, ItemCatalog(repository))
    service.initialize()
    return service


def test_required_trident_workflow_survives_reopen(database_file: Path) -> None:
    first_run = _open_application(database_file)
    campaign = first_run.create_campaign("The Long Road")
    character = first_run.create_character(
        campaign_id=campaign.id,
        name="Mara",
        level=3,
        class_name="Fighter",
        species_name="Human",
        current_hp=24,
        maximum_hp=28,
        notes="Owes the ferryman a favor.",
    )
    trident = first_run.search_catalog("trident")[0]
    first_run.add_inventory(
        character_id=character.id,
        definition_id=trident.id,
        quantity=1,
        notes="Recovered from the river shrine.",
    )

    reopened = _open_application(database_file)
    saved_character = reopened.get_character(character.id)
    saved_inventory = reopened.list_inventory(character.id)

    assert saved_character.current_hp == 24
    assert saved_character.maximum_hp == 28
    assert saved_character.notes == "Owes the ferryman a favor."
    assert len(saved_inventory) == 1
    assert saved_inventory[0].definition.name == "Trident"
    assert saved_inventory[0].instance.quantity == 1
    assert saved_inventory[0].instance.notes == "Recovered from the river shrine."


def test_definition_is_separate_from_character_instances(
    service: CharacterManagerService,
) -> None:
    campaign = service.create_campaign("Salt Marsh")
    first = service.create_character(
        campaign_id=campaign.id,
        name="Iris",
        level=1,
        class_name="Ranger",
        species_name="Elf",
        current_hp=11,
        maximum_hp=11,
    )
    second = service.create_character(
        campaign_id=campaign.id,
        name="Corin",
        level=1,
        class_name="Fighter",
        species_name="Dwarf",
        current_hp=13,
        maximum_hp=13,
    )
    trident = service.search_catalog("trident")[0]

    service.add_inventory(
        character_id=first.id,
        definition_id=trident.id,
        quantity=1,
        notes="Silver cord",
    )
    service.add_inventory(
        character_id=second.id,
        definition_id=trident.id,
        quantity=2,
        notes="Practice pair",
    )

    first_entry = service.list_inventory(first.id)[0]
    second_entry = service.list_inventory(second.id)[0]
    assert first_entry.instance.id != second_entry.instance.id
    assert first_entry.instance.quantity == 1
    assert second_entry.instance.quantity == 2
    assert first_entry.definition is second_entry.definition
    assert service.get_item_definition(trident.id).damage == "1d8"


def test_character_changes_are_committed_immediately(
    service: CharacterManagerService,
) -> None:
    campaign = service.create_campaign("Ash Coast")
    character = service.create_character(
        campaign_id=campaign.id,
        name="Nell",
        level=2,
        class_name="Rogue",
        species_name="Halfling",
        current_hp=14,
        maximum_hp=14,
    )

    service.update_character(
        character_id=character.id,
        name=character.name,
        level=character.level,
        class_name=character.class_name,
        species_name=character.species_name,
        current_hp=6,
        maximum_hp=14,
        notes="Poisoned during the crossing.",
    )

    saved = service.get_character(character.id)
    assert saved.current_hp == 6
    assert saved.notes == "Poisoned during the crossing."


def test_inventory_can_be_updated_and_removed(service: CharacterManagerService) -> None:
    campaign = service.create_campaign("Deep Roads")
    character = service.create_character(
        campaign_id=campaign.id,
        name="Perrin",
        level=1,
        class_name="Fighter",
        species_name="Human",
        current_hp=12,
        maximum_hp=12,
    )
    trident = service.search_catalog("trident")[0]
    instance = service.add_inventory(
        character_id=character.id,
        definition_id=trident.id,
    )

    service.update_inventory(
        instance_id=instance.id,
        quantity=2,
        notes="A matched pair.",
    )
    updated = service.list_inventory(character.id)
    assert updated[0].instance.quantity == 2
    assert updated[0].instance.notes == "A matched pair."

    service.remove_inventory(instance.id)
    assert service.list_inventory(character.id) == []
