"""Menu orchestration services."""
from __future__ import annotations

from typing import Dict, List, Optional

from app.integration.repositories.menu_repository import MenuRepository
from app.ownership.entities.menu import MenuSections


class MenuService:
    def __init__(self, repository: Optional[MenuRepository] = None) -> None:
        self._repository = repository or MenuRepository()

    def menu_overview(self) -> List[Dict[str, object]]:
        return self._repository.fetch_menu_overview()

    def build_sections(self) -> MenuSections:
        pizzas = self._repository.fetch_pizza_details()
        extras = self._repository.fetch_active_menu_items()

        grouped: Dict[str, List[Dict[str, object]]] = {}
        for item in extras:
            group = (item.get("type") or "other").lower()
            grouped.setdefault(group, []).append(item)

        return MenuSections(pizzas=pizzas, extras_by_type=grouped)


__all__ = ["MenuService"]
