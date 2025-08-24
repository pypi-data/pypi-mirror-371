"""PGCopy bynary dump parser."""

from .enums import (
    PGDataType,
    PGDataTypeLength,
    PGOid,
    PGOidToDType,
)
from .errors import (
    PGCopyEOFError,
    PGCopyError,
    PGCopyOidNotSupportError,
    PGCopyRecordError,
    PGCopySignatureError,
)
from .parse import AssociateDtypes
from .structs import PGCopy


__all__ = (
    "AssociateDtypes",
    "PGCopy",
    "PGCopyEOFError",
    "PGCopyError",
    "PGCopyOidNotSupportError",
    "PGCopyRecordError",
    "PGCopySignatureError",
    "PGDataType",
    "PGDataTypeLength",
    "PGOid",
    "PGOidToDType",
)
__author__ = "0xMihalich"
__version__ = "0.0.3"
