from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Role(str, Enum):
    GIAM_SAT = "Giám sát"
    THUC_HIEN = "Thực hiện"
    KIEM_DINH = "Kiểm định"


class Participant(BaseModel):
    name: str
    roles: list[Role] = Field(min_length=1)


class Task(BaseModel):
    content: str
    deadline: str | None
    participants: list[Participant] = Field(min_length=1)


class ChitChatResult(BaseModel):
    type: Literal["chitchat"]
    reply: str


class TaskExtractionResult(BaseModel):
    type: Literal["task_extraction"]
    tasks: list[Task] = Field(min_length=1)


AssignExtractResult = ChitChatResult | TaskExtractionResult
