from io import (
    BufferedReader,
    BufferedWriter,
)
from struct import pack
from typing import Union, TYPE_CHECKING
from zlib import (
    crc32,
    compress,
)

from .compressor import pgcopy_compressor
from .enums import CompressionMethod
from .header import HEADER
from .offset import OffsetOpener

if TYPE_CHECKING:
    from lz4.frame import LZ4FrameFile
    from zstandard import ZstdCompressionWriter


class PGCryptWriter:
    """Class for write PGCrypt format."""

    def __init__(
        self,
        fileobj: BufferedWriter,
        compression_method: CompressionMethod = CompressionMethod.LZ4,
    ) -> None:
        """Class initialization."""

        self.fileobj = fileobj
        self.compression_method = compression_method
        self.metadata_end: int = 0
        self.fileobj_end: int = 0

    def write_metadata(
        self,
        metadata: bytes,
    ) -> int:
        """Make first blocks with metadata."""

        metadata_zlib: bytes = compress(metadata)
        metadata_crc: bytes = pack("!L", crc32(metadata_zlib))
        metadata_length: bytes = pack("!L", len(metadata_zlib))

        self.fileobj.seek(0)
        self.fileobj.write(HEADER)
        self.fileobj.write(metadata_crc)
        self.fileobj.write(metadata_length)
        self.fileobj.write(metadata_zlib)
        self.fileobj.flush()

        self.metadata_end = len(metadata_zlib) + 16

        return self.metadata_end

    def write_pgcopy(
        self,
        pgcopy: BufferedReader,
    ) -> int:
        """Make second blocks with pgcopy."""

        compression_method: bytes = pack("!B", self.compression_method.value)

        self.fileobj.seek(self.metadata_end)
        self.fileobj.write(compression_method)
        self.fileobj.write(bytes(16))  # write empty data for correction later

        offset_opener = OffsetOpener(self.fileobj)
        pgcopy_writer: Union[
            OffsetOpener,
            LZ4FrameFile,
            ZstdCompressionWriter,
        ] = pgcopy_compressor(
            offset_opener,
            self.compression_method,
        )

        if hasattr(pgcopy, "copy_reader"):
            for data in pgcopy.copy_reader():
                pgcopy_writer.write(data)
        else:
            pgcopy_writer.write(pgcopy.read())

        if not isinstance(pgcopy_writer, OffsetOpener):
            pgcopy_writer.close()

        pgcopy_compressed_length: int = offset_opener.tell()
        pgcopy_data_length: int = pgcopy.tell()
        self.fileobj_end: int = self.fileobj.tell()

        self.fileobj.seek(self.metadata_end + 1)
        self.fileobj.write(
            pack("!2Q", pgcopy_compressed_length, pgcopy_data_length)
        )
        self.fileobj.flush()

        return self.fileobj_end

    def write(
        self,
        metadata: bytes,
        pgcopy: BufferedReader,
    ) -> int:
        """Write PGCrypt file."""

        self.write_metadata(metadata)
        self.write_pgcopy(pgcopy)
        self.fileobj.close()

        return self.fileobj_end
