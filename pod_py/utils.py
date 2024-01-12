import yaml
from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True, slots=True, frozen=True)
class Pod:
    name: str
    namespace: str
    manifest: Optional[dict]


