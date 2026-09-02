from ._processor import TranscriptionFailedError, run
from ._schema import Segment, TranscribeResult

__all__ = [
    "Segment",
    "TranscribeResult",
    "TranscriptionFailedError",
    "run",
]
