from struct import unpack
from typing import Union

from .nullables import if_nullable


@if_nullable
def to_point(binary_data: bytes) -> tuple[float, float]:
    """Unpack point value."""

    return unpack("!2d", binary_data)


@if_nullable
def to_line(binary_data: bytes) -> tuple[float, float, float]:
    """Unpack line value."""

    return unpack("!3d", binary_data)


@if_nullable
def to_circle(binary_data: bytes) -> tuple[tuple[float, float], float]:
    """Unpack circle value."""

    *x_y, r = unpack("!3d", binary_data)

    return x_y, r


@if_nullable
def to_lseg(binary_data: bytes) -> list[tuple[float, float]]:
    """Unpack lseg value."""

    x1, y1, x2, y2 = unpack("!4d", binary_data)

    return [(x1, y1), (x2, y2)]


@if_nullable
def to_box(binary_data: bytes) -> tuple[
    tuple[float, float],
    tuple[float, float],
]:
    """Unpack box value."""

    x1, y1, x2, y2 = unpack("!4d", binary_data)

    return (x1, y1), (x2, y2)


@if_nullable
def to_path(binary_data: bytes) -> Union[
    list[tuple[float, float]],
    tuple[tuple[float, float]],
]:
    """Unpack path value."""

    is_closed, length, *path_data = unpack(
        f"!?l{(len(binary_data) - 5) // 8}d",
        binary_data,
    )
    path_data = tuple(
        path_data[i:i + 2]
        for i in range(0, len(path_data), 2)
    )

    return {
        True: tuple,
        False: list,
    }[is_closed](
        path_data[i:i + length]
        for i in range(0, len(path_data), length)
    )


@if_nullable
def to_polygon(binary_data: bytes) -> tuple[tuple[float, float]]:
    """Unpack polygon value."""

    length, *path_data = unpack(
        f"!l{(len(binary_data) - 4) // 8}d",
        binary_data,
    )
    path_data = tuple(
        path_data[i:i + 2]
        for i in range(0, len(path_data), 2)
    )

    return tuple(
        path_data[i:i + length]
        for i in range(0, len(path_data), length)
    )
