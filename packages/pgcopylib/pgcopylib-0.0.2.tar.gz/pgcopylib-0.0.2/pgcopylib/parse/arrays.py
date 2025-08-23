from io import BytesIO
from math import prod
from struct import unpack
from types import FunctionType
from typing import Any

from ..enums import (
    PGDataType,
    PGOid,
    PGOidToDType,
)
from ..errors import PGCopyOidNotSupportError
from ..reader import read_record
from .dates import (
    to_date,
    to_interval,
    to_time,
    to_timestamp,
    to_timestamptz,
    to_timetz,
)
from .digits import (
    to_bool,
    to_float4,
    to_float8,
    to_int2,
    to_int4,
    to_int8,
    to_money,
    to_numeric,
    to_oid,
    to_serial2,
    to_serial4,
    to_serial8,
)
from .geometrics import (
    to_box,
    to_circle,
    to_line,
    to_lseg,
    to_path,
    to_point,
    to_polygon,
)
from .ipaddrs import to_network
from .jsons import to_json
from .nullables import if_nullable
from .strings import (
    to_bits,
    to_bytea,
    to_macaddr,
    to_text,
)
from .uuids import to_uuid


DtypeFunc: dict[PGDataType, FunctionType] = {
    PGDataType.Bit: to_bits,
    PGDataType.Bool: to_bool,
    PGDataType.Box: to_box,
    PGDataType.Bytes: to_bytea,
    PGDataType.Cidr: to_network,
    PGDataType.Circle: to_circle,
    PGDataType.Date: to_date,
    PGDataType.Float4: to_float4,
    PGDataType.Float8: to_float8,
    PGDataType.Inet: to_network,
    PGDataType.Int2: to_int2,
    PGDataType.Int4: to_int4,
    PGDataType.Int8: to_int8,
    PGDataType.Interval: to_interval,
    PGDataType.Json: to_json,
    PGDataType.Line: to_line,
    PGDataType.Lseg: to_lseg,
    PGDataType.Macaddr8: to_macaddr,
    PGDataType.Macaddr: to_macaddr,
    PGDataType.Money: to_money,
    PGDataType.Numeric: to_numeric,
    PGDataType.Oid: to_oid,
    PGDataType.Path: to_path,
    PGDataType.Point: to_point,
    PGDataType.Polygon: to_polygon,
    PGDataType.Serial2: to_serial2,
    PGDataType.Serial4: to_serial4,
    PGDataType.Serial8: to_serial8,
    PGDataType.Text: to_text,
    PGDataType.Time: to_time,
    PGDataType.Timestamp: to_timestamp,
    PGDataType.Timestamptz: to_timestamptz,
    PGDataType.Timetz: to_timetz,
    PGDataType.Uuid: to_uuid,
}


def recursive_elements(
    elements: list[Any],
    array_struct: list[int],
) -> list[Any]:
    """Recursive unpack array struct."""

    if len(array_struct) == 0:
        return elements

    chunk = array_struct.pop()

    if len(elements) == chunk:
        return recursive_elements(elements, array_struct)

    return recursive_elements(
        [
            elements[i:i + chunk]
            for i in range(0, len(elements), chunk)
        ],
        array_struct,
    )


@if_nullable
def to_array(binary_data: bytes) -> list[Any]:
    """Unpack array values."""

    buffer = BytesIO(binary_data)
    nested, _, oid = unpack("!3I", buffer.read(12))

    try:
        array_type = PGOid(oid)
    except ValueError:
        raise PGCopyOidNotSupportError("Oid not support.")

    to_dtype = DtypeFunc[PGOidToDType[array_type]]
    array_struct = [
        unpack("!2I", buffer.read(8))[0]
        for _ in range(nested)
    ]
    elements = [
        to_dtype(read_record(buffer))
        for _ in range(prod(array_struct))
    ]

    return recursive_elements(
        elements,
        array_struct,
    )


AssociateDtypes: dict[PGDataType, FunctionType] = {
    PGDataType.Array: to_array,
    **DtypeFunc,
}
