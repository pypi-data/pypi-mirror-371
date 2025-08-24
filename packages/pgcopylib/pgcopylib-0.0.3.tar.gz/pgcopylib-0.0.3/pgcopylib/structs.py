from io import BufferedReader
from types import FunctionType
from typing import (
    Any,
    Generator,
    Optional,
)
from struct import unpack

from .enums import PGDataType
from .errors import (
    PGCopySignatureError,
    PGCopyEOFError,
    PGCopyError,
)
from .parse import AssociateDtypes
from .reader import (
    read_record,
    skip_record,
)


class PGCopy:
    """PGCopy dump unpacker."""

    def __init__(
        self,
        file: BufferedReader,
        columns: list[str] = [],
        dtypes: list[PGDataType] = [],
        length: Optional[int] = None,
    ) -> None:
        """Class initialization."""

        self.file = file
        self.columns = columns
        self.dtypes = dtypes
        self.length = length

        self.file.seek(0)

        self.header: bytes = self.file.read(11)

        if self.header != b"PGCOPY\n\xff\r\n\x00":
            msg = "PGCopy signature not match!"
            raise PGCopySignatureError(msg)

        self.flags_area: list[int] = [
            (byte >> i) & 1
            for byte in self.file.read(4)
            for i in range(7, -1, -1)
        ]
        self.is_oid_enable: bool = bool(self.flags_area[16])
        self.header_ext_length: int = unpack("!i", self.file.read(4))[0]
        self.num_columns: Optional[int] = None
        self.num_rows: Optional[int] = None

    @staticmethod
    def to_dtypes(reader: FunctionType):
        """Cast data types decorator."""

        def wrapper(*args, **kwargs):

            self: PGCopy = args[0]
            raw: tuple[bytes, int] = reader(*args, **kwargs)

            if self.dtypes:
                to_dtype: FunctionType = AssociateDtypes[self.dtypes[raw[1]]]
                return to_dtype(raw[0])

            return raw[0]

        return wrapper

    def _col_rows(self) -> None:
        """Read columns and rows."""

        if not self.num_columns and not self.num_rows:
            self.file.seek(19)
            self.num_rows = 0

            cols: int = unpack("!h", self.file.read(2))[0]
            all_cols: list[int] = []

            while cols != -1:
                all_cols.append(cols)
                self.num_rows += 1

                if self.is_oid_enable:
                    self.file.seek(self.file.tell() + 4)

                [skip_record(self.file) for _ in range(cols)]
                cols: int = unpack("!h", self.file.read(2))[0]

            self.num_columns = max(all_cols)
            self.columns = self.columns or list(range(self.num_columns))

    @to_dtypes
    def _reader(
        self,
        column: int,
    ) -> tuple[Any, int]:
        """Read record from file."""

        return read_record(self.file), column

    def read_raw(self) -> list[Optional[Any], None, None]:
        """Read single row."""

        cols: int = unpack("!h", self.file.read(2))[0]

        if cols == -1:
            raise PGCopyEOFError("PGCopy end of file!")
        if not cols:
            raise PGCopyError("No columns!")
        if self.is_oid_enable:
            self.file.seek(self.file.tell() + 4)

        return [
            self._reader(column)
            for column in range(cols)
        ]

    def read_raws(self) -> Generator[
        list[Optional[Any]],
        None,
        None,
    ]:
        """Read all rows."""

        while 1:
            try:
                yield self.read_raw()
            except PGCopyEOFError:
                break

    def read(self) -> list[list[bytes]]:
        """Read all raws."""

        self.file.seek(19)
        self._col_rows()

        return list(self.read_raws())

    def __repr__(self) -> str:
        """PGCopy info in interpreter."""

        return self.__str__()

    def __str__(self) -> str:
        """PGCopy info."""

        self._col_rows()

        return f"""PGCopy dump
Total columns: {self.num_columns}
Total raws: {self.num_rows}
Columns: {self.columns}
DTypes: {[dtype.name for dtype in self.dtypes]
         or ["Raw" for _ in range(self.num_columns)]}
"""
