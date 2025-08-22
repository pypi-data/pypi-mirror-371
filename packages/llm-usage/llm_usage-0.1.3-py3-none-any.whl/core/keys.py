from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class KeyAlias:
    alias: str
    value: str


class KeyPool:
    def __init__(self, aliases: List[KeyAlias]):
        self.aliases = aliases

    @classmethod
    def from_values(cls, values: List[str], prefix: str) -> "KeyPool":
        aliases = [KeyAlias(alias=f"{prefix}-{i}", value=v) for i, v in enumerate(values)]
        return cls(aliases)

    def get_by_alias(self, alias: str) -> Optional[KeyAlias]:
        for a in self.aliases:
            if a.alias == alias:
                return a
        return None

    def all_aliases(self) -> List[str]:
        return [a.alias for a in self.aliases]


