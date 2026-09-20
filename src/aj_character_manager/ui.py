"""Flet UI for the Phase 1 desktop vertical slice."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import flet as ft

from .domain import Character, InventoryEntry, ItemDefinition, ValidationError
from .service import CharacterManagerService, NotFoundError

ACCENT = "#6D4C8D"


class CharacterManagerApp:
    def __init__(self, page: ft.Page, service: CharacterManagerService) -> None:
        self.page = page
        self.service = service
        self.current_campaign_id: str | None = None
        self.current_character_id: str | None = None

    def start(self) -> None:
        self.page.title = "AJ's Character Manager"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.theme = ft.Theme(color_scheme_seed=ACCENT, use_material3=True)
        self.page.dark_theme = ft.Theme(color_scheme_seed=ACCENT, use_material3=True)
        self.page.window.width = 1180
        self.page.window.height = 800
        self.page.window.min_width = 760
        self.page.window.min_height = 600
        self.render_campaigns()

    def _click(self, callback: Callable[..., Any], *args: Any) -> Callable[[Any], None]:
        def handler(_: Any) -> None:
            callback(*args)

        return handler

    def _set_content(self, content: ft.Control) -> None:
        self.page.clean()
        self.page.add(
            ft.Container(
                content=content,
                padding=28,
                expand=True,
            )
        )

    def _show_message(self, message: str, *, error: bool = False) -> None:
        self.page.show_dialog(
            ft.SnackBar(
                content=message,
                bgcolor=ft.Colors.ERROR_CONTAINER if error else None,
                show_close_icon=True,
            )
        )

    def _show_error(self, error: Exception) -> None:
        self._show_message(str(error), error=True)

    @staticmethod
    def _header(
        title: str,
        subtitle: str,
        *,
        leading: ft.Control | None = None,
        actions: list[ft.Control] | None = None,
    ) -> ft.Control:
        controls: list[ft.Control] = []
        if leading:
            controls.append(leading)
        controls.append(
            ft.Column(
                [
                    ft.Text(title, size=30, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitle, color=ft.Colors.ON_SURFACE_VARIANT),
                ],
                spacing=2,
                expand=True,
            )
        )
        controls.extend(actions or [])
        return ft.Row(
            controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    @staticmethod
    def _empty_state(icon: ft.IconData, title: str, detail: str) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=48, color=ft.Colors.OUTLINE),
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        detail,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.Alignment.CENTER,
            padding=48,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        )

    def render_campaigns(self) -> None:
        self.current_campaign_id = None
        self.current_character_id = None
        campaigns = self.service.list_campaigns()
        cards: list[ft.Control] = []
        for campaign in campaigns:
            characters = self.service.list_characters(campaign.id)
            cards.append(
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.MAP_OUTLINED, color=ACCENT),
                        title=ft.Text(campaign.name, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            f"{len(characters)} character{'s' if len(characters) != 1 else ''}"
                        ),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=self._click(self.render_campaign, campaign.id),
                    )
                )
            )
        body: ft.Control
        if cards:
            body = ft.ListView(cards, spacing=10, expand=True)
        else:
            body = self._empty_state(
                ft.Icons.CASTLE_OUTLINED,
                "Start a campaign",
                "Create a campaign, then add the characters who adventure together.",
            )
        self._set_content(
            ft.Column(
                [
                    self._header(
                        "AJ's Character Manager",
                        "Local, offline campaign and character tracking",
                        actions=[
                            ft.FilledButton(
                                "New campaign",
                                icon=ft.Icons.ADD,
                                on_click=self._click(self._show_campaign_dialog),
                            )
                        ],
                    ),
                    ft.Divider(height=24),
                    body,
                    ft.Text(
                        "Independent and unofficial. Not affiliated with or endorsed by "
                        "Wizards of the Coast.",
                        size=12,
                        color=ft.Colors.OUTLINE,
                    ),
                ],
                spacing=14,
                expand=True,
            )
        )

    def render_campaign(self, campaign_id: str) -> None:
        try:
            campaign = self.service.get_campaign(campaign_id)
            characters = self.service.list_characters(campaign_id)
        except NotFoundError as error:
            self._show_error(error)
            self.render_campaigns()
            return
        self.current_campaign_id = campaign_id
        self.current_character_id = None
        cards: list[ft.Control] = []
        for character in characters:
            cards.append(
                ft.Card(
                    content=ft.ListTile(
                        leading=ft.Container(
                            content=ft.Text(
                                str(character.level),
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            alignment=ft.Alignment.CENTER,
                            width=44,
                            height=44,
                            border_radius=22,
                            bgcolor=ft.Colors.SECONDARY_CONTAINER,
                        ),
                        title=ft.Text(character.name, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(self._character_summary(character)),
                        trailing=ft.Text(
                            f"{character.current_hp}/{character.maximum_hp} HP",
                            weight=ft.FontWeight.BOLD,
                        ),
                        on_click=self._click(self.render_character, character.id),
                    )
                )
            )
        body: ft.Control
        if cards:
            body = ft.ListView(cards, spacing=10, expand=True)
        else:
            body = self._empty_state(
                ft.Icons.GROUP_OUTLINED,
                "No characters yet",
                "Add the first character to this campaign.",
            )
        self._set_content(
            ft.Column(
                [
                    self._header(
                        campaign.name,
                        "Party dashboard",
                        leading=ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            tooltip="All campaigns",
                            on_click=self._click(self.render_campaigns),
                        ),
                        actions=[
                            ft.FilledButton(
                                "New character",
                                icon=ft.Icons.PERSON_ADD_OUTLINED,
                                on_click=self._click(self._show_character_dialog, campaign_id),
                            )
                        ],
                    ),
                    ft.Divider(height=24),
                    body,
                ],
                spacing=14,
                expand=True,
            )
        )

    def render_character(self, character_id: str) -> None:
        try:
            character = self.service.get_character(character_id)
            campaign = self.service.get_campaign(character.campaign_id)
            inventory = self.service.list_inventory(character_id)
        except NotFoundError as error:
            self._show_error(error)
            self.render_campaigns()
            return
        self.current_campaign_id = character.campaign_id
        self.current_character_id = character_id

        name = ft.TextField(label="Name", value=character.name, col={"sm": 12, "md": 6})
        level = ft.TextField(
            label="Level",
            value=str(character.level),
            keyboard_type=ft.KeyboardType.NUMBER,
            col={"sm": 4, "md": 2},
        )
        class_name = ft.TextField(
            label="Class",
            value=character.class_name,
            col={"sm": 8, "md": 4},
        )
        species_name = ft.TextField(
            label="Species",
            value=character.species_name,
            col={"sm": 12, "md": 6},
        )
        current_hp = ft.TextField(
            label="Current HP",
            value=str(character.current_hp),
            keyboard_type=ft.KeyboardType.NUMBER,
            col={"sm": 6, "md": 3},
        )
        maximum_hp = ft.TextField(
            label="Maximum HP",
            value=str(character.maximum_hp),
            keyboard_type=ft.KeyboardType.NUMBER,
            col={"sm": 6, "md": 3},
        )
        notes = ft.TextField(
            label="Notes",
            value=character.notes,
            multiline=True,
            min_lines=4,
            max_lines=8,
        )

        def save_character(_: Any) -> None:
            try:
                self.service.update_character(
                    character_id=character.id,
                    name=name.value,
                    level=self._required_int(level.value, "Level"),
                    class_name=class_name.value,
                    species_name=species_name.value,
                    current_hp=self._required_int(current_hp.value, "Current HP"),
                    maximum_hp=self._required_int(maximum_hp.value, "Maximum HP"),
                    notes=notes.value,
                )
            except (ValidationError, ValueError) as error:
                self._show_error(error)
                return
            self.render_character(character.id)
            self._show_message("Character saved.")

        profile = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Character", size=20, weight=ft.FontWeight.BOLD),
                        ft.ResponsiveRow(
                            [
                                name,
                                level,
                                class_name,
                                species_name,
                                current_hp,
                                maximum_hp,
                            ],
                            spacing=12,
                            run_spacing=12,
                        ),
                        notes,
                        ft.Row(
                            [
                                ft.FilledButton(
                                    "Save character",
                                    icon=ft.Icons.SAVE_OUTLINED,
                                    on_click=save_character,
                                )
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=14,
                ),
                padding=20,
            )
        )

        inventory_controls: list[ft.Control] = []
        for entry in inventory:
            inventory_controls.append(self._inventory_tile(entry))
        if not inventory_controls:
            inventory_controls.append(
                self._empty_state(
                    ft.Icons.BACKPACK_OUTLINED,
                    "Inventory is empty",
                    "Search the catalog to add equipment.",
                )
            )
        inventory_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text("Inventory", size=20, weight=ft.FontWeight.BOLD),
                                ft.FilledButton(
                                    "Add item",
                                    icon=ft.Icons.ADD,
                                    on_click=self._click(self._show_catalog_dialog, character.id),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Column(inventory_controls, spacing=8),
                    ],
                    spacing=14,
                ),
                padding=20,
            )
        )

        self._set_content(
            ft.Column(
                [
                    self._header(
                        character.name,
                        f"{campaign.name} · {character.current_hp}/{character.maximum_hp} HP",
                        leading=ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            tooltip="Campaign dashboard",
                            on_click=self._click(self.render_campaign, character.campaign_id),
                        ),
                    ),
                    ft.Divider(height=24),
                    ft.ListView([profile, inventory_card], spacing=16, expand=True),
                ],
                spacing=14,
                expand=True,
            )
        )

    @staticmethod
    def _character_summary(character: Character) -> str:
        labels = [f"Level {character.level}"]
        if character.species_name:
            labels.append(character.species_name)
        if character.class_name:
            labels.append(character.class_name)
        return " · ".join(labels)

    def _inventory_tile(self, entry: InventoryEntry) -> ft.Control:
        item = entry.definition
        details = [f"Quantity {entry.instance.quantity}"]
        if item.damage:
            details.append(f"{item.damage} {item.damage_type}")
        if entry.instance.notes:
            details.append(entry.instance.notes)
        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(
                    ft.Icons.HARDWARE_OUTLINED
                    if item.category.endswith("Weapon")
                    else ft.Icons.INVENTORY_2_OUTLINED
                ),
                title=ft.Text(item.name, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(" · ".join(details)),
                trailing=ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.EDIT_OUTLINED,
                            tooltip="Edit inventory item",
                            on_click=self._click(self._show_inventory_dialog, entry),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="Remove inventory item",
                            on_click=self._click(self._confirm_remove_inventory, entry),
                        ),
                    ],
                    tight=True,
                ),
                on_click=self._click(self._show_item_dialog, item, None),
            ),
            border_radius=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        )

    def _show_campaign_dialog(self) -> None:
        name = ft.TextField(label="Campaign name", autofocus=True)

        def create(_: Any) -> None:
            try:
                campaign = self.service.create_campaign(name.value)
            except ValidationError as error:
                self._show_error(error)
                return
            self.page.pop_dialog()
            self.render_campaign(campaign.id)
            self._show_message("Campaign created.")

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title="Create campaign",
                content=name,
                actions=[
                    ft.OutlinedButton("Cancel", on_click=self._click(self.page.pop_dialog)),
                    ft.FilledButton("Create", on_click=create),
                ],
            )
        )

    def _show_character_dialog(self, campaign_id: str) -> None:
        name = ft.TextField(label="Name", autofocus=True)
        level = ft.TextField(label="Level", value="1", keyboard_type=ft.KeyboardType.NUMBER)
        class_name = ft.TextField(label="Class")
        species_name = ft.TextField(label="Species")
        maximum_hp = ft.TextField(
            label="Maximum HP", value="1", keyboard_type=ft.KeyboardType.NUMBER
        )

        def create(_: Any) -> None:
            try:
                maximum = self._required_int(maximum_hp.value, "Maximum HP")
                character = self.service.create_character(
                    campaign_id=campaign_id,
                    name=name.value,
                    level=self._required_int(level.value, "Level"),
                    class_name=class_name.value,
                    species_name=species_name.value,
                    current_hp=maximum,
                    maximum_hp=maximum,
                )
            except (ValidationError, ValueError) as error:
                self._show_error(error)
                return
            self.page.pop_dialog()
            self.render_character(character.id)
            self._show_message("Character created.")

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title="Create character",
                content=ft.Column(
                    [name, level, class_name, species_name, maximum_hp],
                    tight=True,
                    spacing=12,
                    width=440,
                ),
                actions=[
                    ft.OutlinedButton("Cancel", on_click=self._click(self.page.pop_dialog)),
                    ft.FilledButton("Create", on_click=create),
                ],
            )
        )

    def _show_catalog_dialog(self, character_id: str) -> None:
        result_list = ft.ListView(spacing=4, height=390)

        def fill_results(query: str) -> None:
            result_list.controls = []
            for item in self.service.search_catalog(query):
                origin = "Custom" if item.source_kind == "custom" else "SRD 5.2.1"
                result_list.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.SEARCH),
                        title=ft.Text(item.name, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"{item.category} · {origin}"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=self._click(self._open_item_from_catalog, item, character_id),
                    )
                )

        def search_changed(event: Any) -> None:
            fill_results(event.control.value)
            self.page.update(result_list)

        search = ft.TextField(
            label="Search equipment",
            hint_text="Try “trident”",
            prefix_icon=ft.Icons.SEARCH,
            autofocus=True,
            on_change=search_changed,
        )
        fill_results("")
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title="Add an item",
                content=ft.Column(
                    [
                        search,
                        ft.Row(
                            [
                                ft.Text(
                                    "15 reviewed SRD weapons plus your custom items",
                                    size=12,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                ft.OutlinedButton(
                                    "Create custom item",
                                    icon=ft.Icons.ADD,
                                    on_click=self._click(
                                        self._open_custom_item_from_catalog, character_id
                                    ),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        result_list,
                    ],
                    tight=True,
                    width=620,
                ),
                actions=[ft.OutlinedButton("Close", on_click=self._click(self.page.pop_dialog))],
            )
        )

    def _open_item_from_catalog(self, item: ItemDefinition, character_id: str) -> None:
        self.page.pop_dialog()
        self._show_item_dialog(item, character_id)

    def _open_custom_item_from_catalog(self, character_id: str) -> None:
        self.page.pop_dialog()
        self._show_custom_item_dialog(character_id)

    def _show_item_dialog(self, item: ItemDefinition, character_id: str | None) -> None:
        quantity = ft.TextField(label="Quantity", value="1", keyboard_type=ft.KeyboardType.NUMBER)
        notes = ft.TextField(label="Inventory notes", multiline=True, min_lines=2)
        property_text = ", ".join(item.properties) or "—"
        facts = ft.Column(
            [
                self._fact("Category", item.category),
                self._fact(
                    "Damage",
                    f"{item.damage} {item.damage_type}" if item.damage else "—",
                ),
                self._fact("Properties", property_text),
                self._fact("Mastery", item.mastery or "—"),
                self._fact("Weight", item.weight_label),
                self._fact("Cost", item.cost_label),
                self._fact("Source", item.source_reference),
                ft.Text(item.description, color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            spacing=8,
        )
        actions: list[ft.Control] = [
            ft.OutlinedButton("Close", on_click=self._click(self.page.pop_dialog))
        ]
        content_controls: list[ft.Control] = [facts]
        if character_id:
            content_controls.extend([ft.Divider(), quantity, notes])

            def add(_: Any) -> None:
                try:
                    self.service.add_inventory(
                        character_id=character_id,
                        definition_id=item.id,
                        quantity=self._required_int(quantity.value, "Quantity"),
                        notes=notes.value,
                    )
                except (ValidationError, ValueError, NotFoundError) as error:
                    self._show_error(error)
                    return
                self.page.pop_dialog()
                self.render_character(character_id)
                self._show_message(f"Added {item.name}.")

            actions.append(ft.FilledButton("Add to inventory", on_click=add))
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=item.name,
                content=ft.Column(content_controls, tight=True, width=500, spacing=12),
                actions=actions,
                scrollable=True,
            )
        )

    @staticmethod
    def _fact(label: str, value: str) -> ft.Control:
        return ft.Row(
            [
                ft.Text(label, width=90, weight=ft.FontWeight.BOLD),
                ft.Text(value, selectable=True, expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def _show_inventory_dialog(self, entry: InventoryEntry) -> None:
        quantity = ft.TextField(
            label="Quantity",
            value=str(entry.instance.quantity),
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        notes = ft.TextField(
            label="Inventory notes",
            value=entry.instance.notes,
            multiline=True,
            min_lines=3,
        )

        def save(_: Any) -> None:
            try:
                self.service.update_inventory(
                    instance_id=entry.instance.id,
                    quantity=self._required_int(quantity.value, "Quantity"),
                    notes=notes.value,
                )
            except (ValidationError, ValueError, NotFoundError) as error:
                self._show_error(error)
                return
            self.page.pop_dialog()
            self.render_character(entry.instance.character_id)
            self._show_message("Inventory item saved.")

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=f"Edit {entry.definition.name}",
                content=ft.Column([quantity, notes], tight=True, width=420, spacing=12),
                actions=[
                    ft.OutlinedButton("Cancel", on_click=self._click(self.page.pop_dialog)),
                    ft.FilledButton("Save", on_click=save),
                ],
            )
        )

    def _confirm_remove_inventory(self, entry: InventoryEntry) -> None:
        def remove(_: Any) -> None:
            try:
                self.service.remove_inventory(entry.instance.id)
            except NotFoundError as error:
                self._show_error(error)
                return
            self.page.pop_dialog()
            self.render_character(entry.instance.character_id)
            self._show_message(f"Removed {entry.definition.name}.")

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title="Remove item?",
                content=ft.Text(f"Remove {entry.definition.name} from this character's inventory?"),
                actions=[
                    ft.OutlinedButton("Cancel", on_click=self._click(self.page.pop_dialog)),
                    ft.FilledButton("Remove", on_click=remove),
                ],
            )
        )

    def _show_custom_item_dialog(self, character_id: str) -> None:
        name = ft.TextField(label="Name", autofocus=True)
        category = ft.TextField(label="Category", value="Custom Item")
        damage = ft.TextField(label="Damage (optional)", hint_text="For example, 1d6")
        damage_type = ft.TextField(label="Damage type (optional)")
        properties = ft.TextField(label="Properties (optional)", hint_text="Comma-separated")
        mastery = ft.TextField(label="Mastery (optional)")
        weight = ft.TextField(
            label="Weight in lb. (optional)",
            keyboard_type=ft.KeyboardType.NUMBER,
            col={"xs": 12, "sm": 5},
        )
        cost = ft.TextField(
            label="Cost amount (optional)",
            keyboard_type=ft.KeyboardType.NUMBER,
            col={"xs": 12, "sm": 4},
        )
        cost_unit = ft.TextField(label="Cost unit", value="gp", col={"xs": 12, "sm": 3})
        description = ft.TextField(label="Description", multiline=True, min_lines=3, max_lines=6)

        def create(_: Any) -> None:
            try:
                item = self.service.create_custom_item(
                    name=name.value,
                    category=category.value,
                    damage=damage.value,
                    damage_type=damage_type.value,
                    properties=tuple(value.strip() for value in properties.value.split(",")),
                    mastery=mastery.value,
                    weight=self._optional_float(weight.value, "Weight"),
                    cost_quantity=self._optional_int(cost.value, "Cost"),
                    cost_unit=cost_unit.value,
                    description=description.value,
                )
            except (ValidationError, ValueError) as error:
                self._show_error(error)
                return
            self.page.pop_dialog()
            self.render_character(character_id)
            self._show_message(f"Created {item.name}. Add it from the item catalog.")

        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title="Create custom item",
                content=ft.Column(
                    [
                        name,
                        category,
                        ft.Row([damage, damage_type]),
                        properties,
                        mastery,
                        ft.ResponsiveRow([weight, cost, cost_unit], spacing=10, run_spacing=10),
                        description,
                        ft.Text(
                            "This definition is stored locally and appears in catalog searches.",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                    ],
                    tight=True,
                    width=620,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.OutlinedButton("Cancel", on_click=self._click(self.page.pop_dialog)),
                    ft.FilledButton("Create item", on_click=create),
                ],
                scrollable=True,
            )
        )

    @staticmethod
    def _required_int(value: str, label: str) -> int:
        try:
            return int(value.strip())
        except ValueError as error:
            raise ValidationError(f"{label} must be a whole number.") from error

    @staticmethod
    def _optional_int(value: str, label: str) -> int | None:
        if not value.strip():
            return None
        return CharacterManagerApp._required_int(value, label)

    @staticmethod
    def _optional_float(value: str, label: str) -> float | None:
        if not value.strip():
            return None
        try:
            return float(value.strip())
        except ValueError as error:
            raise ValidationError(f"{label} must be a number.") from error
