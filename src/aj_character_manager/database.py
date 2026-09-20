"""SQLite persistence for the Phase 1 vertical slice."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .domain import Campaign, Character, InventoryInstance, ItemDefinition

MIGRATIONS: tuple[tuple[int, str, tuple[str, ...]], ...] = (
    (
        1,
        "phase_1_core",
        (
            """
            CREATE TABLE campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE characters (
                id TEXT PRIMARY KEY,
                campaign_id TEXT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 20),
                class_name TEXT NOT NULL DEFAULT '',
                species_name TEXT NOT NULL DEFAULT '',
                current_hp INTEGER NOT NULL CHECK (current_hp >= 0),
                maximum_hp INTEGER NOT NULL CHECK (maximum_hp >= 1),
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                CHECK (current_hp <= maximum_hp)
            )
            """,
            """
            CREATE INDEX characters_campaign_id_index
            ON characters(campaign_id)
            """,
            """
            CREATE TABLE custom_item_definitions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                category TEXT NOT NULL CHECK (length(trim(category)) > 0),
                damage TEXT NOT NULL DEFAULT '',
                damage_type TEXT NOT NULL DEFAULT '',
                properties_json TEXT NOT NULL DEFAULT '[]',
                mastery TEXT NOT NULL DEFAULT '',
                weight REAL CHECK (weight IS NULL OR weight >= 0),
                cost_quantity INTEGER CHECK (cost_quantity IS NULL OR cost_quantity >= 0),
                cost_unit TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                source_reference TEXT NOT NULL DEFAULT 'Created locally',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE inventory_instances (
                id TEXT PRIMARY KEY,
                character_id TEXT NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
                definition_id TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity >= 1),
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX inventory_character_id_index
            ON inventory_instances(character_id)
            """,
        ),
    ),
)


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class SQLiteRepository:
    """Owns database initialization and persistence operations."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                )
                """
            )
            connection.commit()
            applied = {
                row["version"]: row["checksum"]
                for row in connection.execute("SELECT version, checksum FROM schema_migrations")
            }
            for version, name, statements in MIGRATIONS:
                checksum = hashlib.sha256("\n".join(statements).encode()).hexdigest()
                if version in applied:
                    if applied[version] != checksum:
                        raise RuntimeError(f"Migration {version} checksum does not match.")
                    continue
                try:
                    connection.execute("BEGIN IMMEDIATE")
                    for statement in statements:
                        connection.execute(statement)
                    connection.execute(
                        """
                        INSERT INTO schema_migrations(version, name, checksum, applied_at)
                        VALUES (?, ?, ?, ?)
                        """,
                        (version, name, checksum, _now()),
                    )
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise

    def list_campaigns(self) -> list[Campaign]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM campaigns ORDER BY name COLLATE NOCASE, created_at"
            ).fetchall()
        return [self._campaign(row) for row in rows]

    def create_campaign(self, name: str) -> Campaign:
        campaign_id = str(uuid4())
        timestamp = _now()
        with self._connection() as connection, connection:
            connection.execute(
                """
                INSERT INTO campaigns(id, name, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (campaign_id, name, timestamp, timestamp),
            )
        return Campaign(campaign_id, name, timestamp, timestamp)

    def get_campaign(self, campaign_id: str) -> Campaign | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM campaigns WHERE id = ?", (campaign_id,)
            ).fetchone()
        return self._campaign(row) if row else None

    def list_characters(self, campaign_id: str) -> list[Character]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM characters
                WHERE campaign_id = ?
                ORDER BY name COLLATE NOCASE, created_at
                """,
                (campaign_id,),
            ).fetchall()
        return [self._character(row) for row in rows]

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
        notes: str,
    ) -> Character:
        character_id = str(uuid4())
        timestamp = _now()
        with self._connection() as connection, connection:
            connection.execute(
                """
                INSERT INTO characters(
                    id, campaign_id, name, level, class_name, species_name,
                    current_hp, maximum_hp, notes, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    character_id,
                    campaign_id,
                    name,
                    level,
                    class_name,
                    species_name,
                    current_hp,
                    maximum_hp,
                    notes,
                    timestamp,
                    timestamp,
                ),
            )
        return Character(
            character_id,
            campaign_id,
            name,
            level,
            class_name,
            species_name,
            current_hp,
            maximum_hp,
            notes,
            timestamp,
            timestamp,
        )

    def get_character(self, character_id: str) -> Character | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM characters WHERE id = ?", (character_id,)
            ).fetchone()
        return self._character(row) if row else None

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
    ) -> Character | None:
        timestamp = _now()
        with self._connection() as connection, connection:
            cursor = connection.execute(
                """
                UPDATE characters
                SET name = ?, level = ?, class_name = ?, species_name = ?,
                    current_hp = ?, maximum_hp = ?, notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    name,
                    level,
                    class_name,
                    species_name,
                    current_hp,
                    maximum_hp,
                    notes,
                    timestamp,
                    character_id,
                ),
            )
        if cursor.rowcount == 0:
            return None
        return self.get_character(character_id)

    def list_custom_items(self) -> list[ItemDefinition]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM custom_item_definitions ORDER BY name COLLATE NOCASE"
            ).fetchall()
        return [self._custom_item(row) for row in rows]

    def get_custom_item(self, definition_id: str) -> ItemDefinition | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM custom_item_definitions WHERE id = ?",
                (definition_id,),
            ).fetchone()
        return self._custom_item(row) if row else None

    def create_custom_item(
        self,
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
    ) -> ItemDefinition:
        definition_id = f"local:item:{uuid4()}"
        timestamp = _now()
        with self._connection() as connection, connection:
            connection.execute(
                """
                INSERT INTO custom_item_definitions(
                    id, name, category, damage, damage_type, properties_json,
                    mastery, weight, cost_quantity, cost_unit, description,
                    source_reference, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    definition_id,
                    name,
                    category,
                    damage,
                    damage_type,
                    json.dumps(properties),
                    mastery,
                    weight,
                    cost_quantity,
                    cost_unit,
                    description,
                    "Created locally",
                    timestamp,
                    timestamp,
                ),
            )
        item = self.get_custom_item(definition_id)
        if item is None:  # pragma: no cover - defensive database invariant
            raise RuntimeError("The custom item was not persisted.")
        return item

    def list_inventory(self, character_id: str) -> list[InventoryInstance]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM inventory_instances
                WHERE character_id = ?
                ORDER BY created_at, id
                """,
                (character_id,),
            ).fetchall()
        return [self._inventory(row) for row in rows]

    def add_inventory(
        self,
        *,
        character_id: str,
        definition_id: str,
        quantity: int,
        notes: str,
    ) -> InventoryInstance:
        instance_id = str(uuid4())
        timestamp = _now()
        with self._connection() as connection, connection:
            connection.execute(
                """
                INSERT INTO inventory_instances(
                    id, character_id, definition_id, quantity, notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    instance_id,
                    character_id,
                    definition_id,
                    quantity,
                    notes,
                    timestamp,
                    timestamp,
                ),
            )
        return InventoryInstance(
            instance_id,
            character_id,
            definition_id,
            quantity,
            notes,
            timestamp,
            timestamp,
        )

    def update_inventory(
        self, *, instance_id: str, quantity: int, notes: str
    ) -> InventoryInstance | None:
        timestamp = _now()
        with self._connection() as connection, connection:
            cursor = connection.execute(
                """
                UPDATE inventory_instances
                SET quantity = ?, notes = ?, updated_at = ?
                WHERE id = ?
                """,
                (quantity, notes, timestamp, instance_id),
            )
        if cursor.rowcount == 0:
            return None
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM inventory_instances WHERE id = ?", (instance_id,)
            ).fetchone()
        return self._inventory(row) if row else None

    def remove_inventory(self, instance_id: str) -> bool:
        with self._connection() as connection, connection:
            cursor = connection.execute(
                "DELETE FROM inventory_instances WHERE id = ?", (instance_id,)
            )
        return cursor.rowcount > 0

    @staticmethod
    def _campaign(row: sqlite3.Row) -> Campaign:
        return Campaign(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _character(row: sqlite3.Row) -> Character:
        return Character(
            id=row["id"],
            campaign_id=row["campaign_id"],
            name=row["name"],
            level=row["level"],
            class_name=row["class_name"],
            species_name=row["species_name"],
            current_hp=row["current_hp"],
            maximum_hp=row["maximum_hp"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _custom_item(row: sqlite3.Row) -> ItemDefinition:
        return ItemDefinition(
            id=row["id"],
            source_kind="custom",
            name=row["name"],
            category=row["category"],
            damage=row["damage"],
            damage_type=row["damage_type"],
            properties=tuple(json.loads(row["properties_json"])),
            mastery=row["mastery"],
            weight=row["weight"],
            cost_quantity=row["cost_quantity"],
            cost_unit=row["cost_unit"],
            description=row["description"],
            source_reference=row["source_reference"],
        )

    @staticmethod
    def _inventory(row: sqlite3.Row) -> InventoryInstance:
        return InventoryInstance(
            id=row["id"],
            character_id=row["character_id"],
            definition_id=row["definition_id"],
            quantity=row["quantity"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
