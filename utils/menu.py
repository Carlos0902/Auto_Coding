from nicegui import ui
from typing import List, Dict

class Menu():
    """Class to manage a simple editable menu"""
    def __init__(self, items: list = None):
        self.menu_items = []
        if isinstance(items, list):
            for i, item in enumerate(items):
                self.menu_items.append({"id": str(i), "name": item})
        self.menu_display = ui.column().classes("w-full")
        self.refresh_menu()

    def create_menu_display(self):
        """Create the visual representation of the menu with reordering and delete options"""
        self.menu_column = ui.column().classes("w-full gap-1")
        for item in self.menu_items:
            with ui.row().classes("items-center w-full border rounded p-2 gap-4") as item_row:
                # Reorder buttons
                with ui.column().classes("gap-0"):
                    ui.icon("keyboard_arrow_up", size="sm").on("click", lambda _, i=item: self.move_item_up(i)).classes("cursor-pointer")
                    ui.icon("keyboard_arrow_down", size="sm").on("click", lambda _, i=item: self.move_item_down(i)).classes("cursor-pointer")
                
                # Menu item label
                ui.label(item["name"]).classes("flex-grow")
                
                # Delete button
                ui.icon("delete", size="sm").on("click", lambda _, i=item: self.delete_item(i)).classes("cursor-pointer text-red")

    def move_item_up(self, item: Dict[str, str]):
        """Move an item up in the list"""
        index = next((i for i, x in enumerate(self.menu_items) if x["id"] == item["id"]), None)
        if index is not None and index > 0:
            self.menu_items[index], self.menu_items[index-1] = self.menu_items[index-1], self.menu_items[index]
            self.refresh_menu()

    def move_item_down(self, item: Dict[str, str]):
        """Move an item down in the list"""
        index = next((i for i, x in enumerate(self.menu_items) if x["id"] == item["id"]), None)
        if index is not None and index < len(self.menu_items) - 1:
            self.menu_items[index], self.menu_items[index+1] = self.menu_items[index+1], self.menu_items[index]
            self.refresh_menu()

    def delete_item(self, item: Dict[str, str]):
        """Remove an item from the menu"""
        self.menu_items[:] = [x for x in self.menu_items if x["id"] != item["id"]]
        self.refresh_menu()

    def add_new_item(self, new_item: str):
        """Add a new item to the menu"""
        assert new_item is not None, "Item name cannot be None"
        new_id = str(max(int(item["id"]) for item in self.menu_items) + 1) if self.menu_items else "1"
        self.menu_items.append({"id": new_id, "name": new_item})
        self.refresh_menu()

    def refresh_menu(self):
        """Refresh the menu display"""
        self.menu_display.clear()
        with self.menu_display:
            self.create_menu_display()

if __name__ in {"__main__", "__mp_main__"}:
    menu = Menu(items=["Item 1", "Item 2", "Item 3"])
    ui.run(title='Menu', layout='fit')