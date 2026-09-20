from __future__ import annotations

from pathlib import Path

from aj_character_manager.catalog import ItemCatalog
from aj_character_manager.database import SQLiteRepository
from aj_character_manager.service import CharacterManagerService


def test_custom_item_uses_catalog_boundary_and_survives_reopen(
    service: CharacterManagerService, database_file: Path
) -> None:
    custom_item = service.create_custom_item(
        name="Stormglass Rod",
        category="Custom Weapon",
        damage="1d6",
        damage_type="Lightning",
        properties=("Light",),
        weight=2.5,
        cost_quantity=30,
        cost_unit="gp",
        description="A local test item.",
    )

    assert service.search_catalog("stormglass") == [custom_item]
    assert service.search_catalog("lightning") == [custom_item]

    repository = SQLiteRepository(database_file)
    reopened = CharacterManagerService(repository, ItemCatalog(repository))
    reopened.initialize()

    assert reopened.get_item_definition(custom_item.id) == custom_item
