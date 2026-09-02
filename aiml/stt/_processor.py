from __future__ import annotations

import time
from typing import BinaryIO

from soniox.types import CreateTranscriptionConfig, Token

from .io_adapter import IOBaseAdapter
from ._schema import Segment, TranscribeResult
from .soniox_client import get_client


class TranscriptionFailedError(Exception):
    """Raised when Soniox finishes processing but the result is not usable."""


def _group_into_segments(tokens: list[Token]) -> list[Segment]:
    """Gộp các token liên tiếp cùng speaker + cùng language thành 1 đoạn."""
    segments: list[Segment] = []
    for tok in tokens:
        if not segments or (segments[-1].speaker, segments[-1].language) != (
            tok.speaker,
            tok.language,
        ):
            segments.append(
                Segment(
                    speaker=tok.speaker,
                    language=tok.language,
                    text="",
                    start_ms=tok.start_ms,
                    end_ms=tok.end_ms,
                )
            )
        segments[-1].text += tok.text
        segments[-1].end_ms = tok.end_ms
    return segments


def run(file: BinaryIO, filename: str | None) -> TranscribeResult:
    """
    Gui file audio (file-like, sync, vd SpooledTemporaryFile cua FastAPI) len
    Soniox, cho toi khi xu ly xong, tra ve transcript, roi don sach
    transcription + file da upload tren Soniox.

    Raises:
        soniox.errors.SonioxAPIError: loi tu phia Soniox API.
        TranscriptionFailedError: Soniox xu ly xong nhung ket qua khong dung "completed".
        TimeoutError: cho qua wait_timeout_sec ma van chua xong.
    """
    client = get_client()
    started_at = time.perf_counter()
    transcription = client.stt.transcribe(
        model="stt-async-v5",
        file=IOBaseAdapter(file),
        filename=filename,
        config=CreateTranscriptionConfig(
            language_hints=["vi"],
            enable_speaker_diarization=True,
            enable_language_identification=True,
        ),
    )
    try:
        result = client.stt.wait(transcription.id, timeout_sec=600)
        if result.status != "completed":
            raise TranscriptionFailedError(
                result.error_message or f"Transcription failed with status: {result.status}"
            )
        transcript = client.stt.get_transcript(transcription.id)
    finally:
        # Dọn transcript + file đã upload trên Soniox, không giữ lại gì.
        client.stt.delete_if_exists(transcription.id)
        if transcription.file_id:
            client.files.delete_if_exists(transcription.file_id)

    return TranscribeResult(
        text=transcript.text,
        segments=_group_into_segments(transcript.tokens),
        processing_time_ms=round((time.perf_counter() - started_at) * 1000),
    )
