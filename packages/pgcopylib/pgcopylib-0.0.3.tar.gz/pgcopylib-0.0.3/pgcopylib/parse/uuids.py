from uuid import UUID

from .nullables import if_nullable


@if_nullable
def to_uuid(binary_data: bytes) -> UUID:
    """Unpack uuid value."""

    return UUID(bytes=binary_data)
