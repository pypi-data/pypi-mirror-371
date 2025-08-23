from decimal import Decimal
from struct import (
    unpack,
    unpack_from,
)

from .nullables import if_nullable


@if_nullable
def to_bool(binary_data: bytes) -> bool:
    """Unpack bool value."""

    return unpack("!?", binary_data)[0]


@if_nullable
def to_oid(binary_data: bytes) -> int:
    """Unpack oid value."""

    return unpack("!I", binary_data)[0]


@if_nullable
def to_serial2(binary_data: bytes) -> int:
    """Unpack serial2 value."""

    return unpack("!H", binary_data)[0]


@if_nullable
def to_serial4(binary_data: bytes) -> int:
    """Unpack serial4 value."""

    return unpack("!L", binary_data)[0]


@if_nullable
def to_serial8(binary_data: bytes) -> int:
    """Unpack serial8 value."""

    return unpack("!Q", binary_data)[0]


@if_nullable
def to_int2(binary_data: bytes) -> int:
    """Unpack int2 value."""

    return unpack("!h", binary_data)[0]


@if_nullable
def to_int4(binary_data: bytes) -> int:
    """Unpack int4 value."""

    return unpack("!l", binary_data)[0]


@if_nullable
def to_int8(binary_data: bytes) -> int:
    """Unpack int8 value."""

    return unpack("!q", binary_data)[0]


@if_nullable
def to_money(binary_data: bytes) -> float:
    """Unpack money value."""

    return to_int8(binary_data) * 0.01


@if_nullable
def to_float4(binary_data: bytes) -> float:
    """Unpack float4 value."""

    return unpack("!f", binary_data)[0]


@if_nullable
def to_float8(binary_data: bytes) -> float:
    """Unpack float8 value."""

    return unpack("!d", binary_data)[0]


@if_nullable
def to_numeric(binary_data: bytes) -> Decimal:
    """Unpack numeric value."""

    ndigits, weight, sign, dscale = unpack_from(
        "!hhhh",
        binary_data,
    )

    if sign == 0xc000:
        return Decimal("nan")

    is_negative: bool = sign == 0x4000
    digits: list[int] = [
        unpack_from("!h", binary_data[i:i + 2])[-1]
        for i in range(8, 8 + ndigits * 2, 2)
    ]

    numeric = Decimal(0)
    scale = Decimal(10) ** -dscale

    for pos, digit in enumerate(digits):
        power = Decimal(4) * (Decimal(weight) - Decimal(pos))
        term = Decimal(digit) * (Decimal(10) ** power)
        numeric += term

    if is_negative:
        numeric *= -1

    return numeric.quantize(scale)
