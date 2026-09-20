from __future__ import annotations

import pytest

from aj_character_manager.domain import ValidationError
from aj_character_manager.service import CharacterManagerService


def test_rejects_current_hp_above_maximum(service: CharacterManagerService) -> None:
    campaign = service.create_campaign("Test Campaign")

    with pytest.raises(ValidationError, match="Current HP"):
        service.create_character(
            campaign_id=campaign.id,
            name="Hero",
            level=1,
            class_name="Fighter",
            species_name="Human",
            current_hp=11,
            maximum_hp=10,
        )


def test_rejects_zero_inventory_quantity(service: CharacterManagerService) -> None:
    campaign = service.create_campaign("Test Campaign")
    character = service.create_character(
        campaign_id=campaign.id,
        name="Hero",
        level=1,
        class_name="Fighter",
        species_name="Human",
        current_hp=10,
        maximum_hp=10,
    )
    trident = service.search_catalog("trident")[0]

    with pytest.raises(ValidationError, match="Quantity"):
        service.add_inventory(
            character_id=character.id,
            definition_id=trident.id,
            quantity=0,
        )
