from __future__ import annotations

from aj_character_manager.catalog import BUILTIN_ITEMS
from aj_character_manager.service import CharacterManagerService


def test_reviewed_catalog_has_expected_size_and_unique_ids() -> None:
    assert len(BUILTIN_ITEMS) == 15
    assert len({item.id for item in BUILTIN_ITEMS}) == len(BUILTIN_ITEMS)


def test_trident_matches_srd_5_2_1_weapon_table(
    service: CharacterManagerService,
) -> None:
    results = service.search_catalog("trident")

    assert len(results) == 1
    trident = results[0]
    assert trident.name == "Trident"
    assert trident.damage == "1d8"
    assert trident.damage_type == "Piercing"
    assert trident.properties == ("Thrown (20/60)", "Versatile (1d10)")
    assert trident.mastery == "Topple"
    assert trident.weight == 4
    assert trident.cost_label == "5 GP"
    assert trident.source_reference == "SRD 5.2.1, Weapons table, page 91"


def test_catalog_searches_more_than_item_names(service: CharacterManagerService) -> None:
    assert {item.name for item in service.search_catalog("topple")} == {
        "Battleaxe",
        "Quarterstaff",
        "Trident",
    }
