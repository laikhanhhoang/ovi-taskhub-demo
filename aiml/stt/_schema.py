from __future__ import annotations

from pydantic import BaseModel


class Segment(BaseModel):
    speaker: str | None
    language: str | None
    text: str
    start_ms: int | None
    end_ms: int | None


class TranscribeResult(BaseModel):
    text: str
    segments: list[Segment]
    processing_time_ms: int
