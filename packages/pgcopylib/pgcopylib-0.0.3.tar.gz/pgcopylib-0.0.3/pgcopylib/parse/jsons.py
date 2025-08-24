from json import loads
from typing import TypeAlias

from .nullables import if_nullable


Json: TypeAlias = dict[str, "Json"]|list["Json"]|str|int|float|bool|None


@if_nullable
def to_json(binary_data: bytes) -> Json:
    """Unpack json value."""

    return loads(binary_data)
