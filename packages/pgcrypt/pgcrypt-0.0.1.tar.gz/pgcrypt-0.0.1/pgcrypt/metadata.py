from json import loads

from pgcopylib import (
    PGOid,
    PGOidToDType,
    PGDataType,
)


def metadata_reader(metadata: bytes) -> tuple[list[str], list[PGDataType]]:
    """Read columns and data types from unpacked metadata."""

    metadata_info: list[list[int, list[str, int]]] = loads(metadata)
    columns_data: dict[int, list[str, int]] = {
        column: name_dtype
        for column, name_dtype in metadata_info
    }
    num_columns: int = len(columns_data)

    return [
        columns_data[num_column][0]
        for num_column in range(1, num_columns + 1)
    ], [
        PGOidToDType[PGOid(columns_data[num_column][1])]
        for num_column in range(1, num_columns + 1)
    ]
