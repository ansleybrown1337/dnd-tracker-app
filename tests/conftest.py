from __future__ import annotations

from pathlib import Path

import pytest

from aj_character_manager.catalog import ItemCatalog
from aj_character_manager.database import SQLiteRepository
from aj_character_manager.service import CharacterManagerService


@pytest.fixture
def database_file(tmp_path: Path) -> Path:
    return tmp_path / "character-manager.sqlite3"


@pytest.fixture
def service(database_file: Path) -> CharacterManagerService:
    repository = SQLiteRepository(database_file)
    application = CharacterManagerService(repository, ItemCatalog(repository))
    application.initialize()
    return application
