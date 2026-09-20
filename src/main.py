"""Flet entry point for AJ's Character Manager."""

from __future__ import annotations

import flet as ft

from aj_character_manager.catalog import ItemCatalog
from aj_character_manager.database import SQLiteRepository
from aj_character_manager.paths import database_path
from aj_character_manager.service import CharacterManagerService
from aj_character_manager.ui import CharacterManagerApp


def main(page: ft.Page) -> None:
    repository = SQLiteRepository(database_path())
    service = CharacterManagerService(repository, ItemCatalog(repository))
    service.initialize()
    CharacterManagerApp(page, service).start()


if __name__ == "__main__":
    ft.run(main)
