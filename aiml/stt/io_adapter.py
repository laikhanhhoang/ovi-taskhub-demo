from __future__ import annotations

import io
from typing import BinaryIO


class IOBaseAdapter(io.RawIOBase):
    """Wrap any file-like object (e.g. Starlette's SpooledTemporaryFile) as a real io.IOBase.

    SpooledTemporaryFile doesn't subclass io.IOBase (it just duck-types the
    file protocol), but the Soniox SDK requires an io.IOBase instance for
    streaming uploads. This forwards reads without buffering the file.
    """

    def __init__(self, fp: BinaryIO) -> None:
        self._fp = fp

    def readable(self) -> bool:
        return True

    def readinto(self, b: bytearray) -> int:
        data = self._fp.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def seekable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._fp.seek(offset, whence)

    def tell(self) -> int:
        return self._fp.tell()
