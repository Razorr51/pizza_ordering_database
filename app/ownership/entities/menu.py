"""Domain entities for menu presentation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MenuSections:
    """Grouped menu items ready for rendering."""

    pizzas: List[Dict[str, object]]
    extras_by_type: Dict[str, List[Dict[str, object]]] = field(default_factory=dict)

    def category(self, name: str) -> List[Dict[str, object]]:
        """Return extras for the requested category name."""
        return self.extras_by_type.get(name, [])


__all__ = ["MenuSections"]
