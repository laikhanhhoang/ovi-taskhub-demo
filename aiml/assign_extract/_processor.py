from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from ._schema import AssignExtractResult, ChitChatResult, TaskExtractionResult
from .llm_client import get_client, get_model


class ExtractionFailedError(Exception):
    """Raised when the LLM does not return a usable report_result call."""


_SYSPROMPT_TEMPLATE = (Path(__file__).parent / "_sysprompt.txt").read_text(encoding="utf-8")

_TASK_ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "content": {"type": "string", "description": "Nội dung đầu việc."},
        "deadline": {
            "type": ["string", "null"],
            "description": "Cụm từ chỉ thời hạn, ghi nguyên văn theo cách người dùng nói (vd 'trước thứ 6', 'cuối tuần này') nếu câu có đề cập, ngược lại null. Không tự quy đổi thành ngày tháng cụ thể.",
        },
        "participants": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Tên người tham gia đầu việc."},
                    "roles": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "enum": ["Giám sát", "Thực hiện", "Kiểm định"]},
                        "description": "Một hoặc nhiều chức vụ mà người này nắm giữ trong đầu việc.",
                    },
                },
                "required": ["name", "roles"],
                "additionalProperties": False,
            },
            "description": "Danh sách người tham gia đầu việc, mỗi người kèm chức vụ.",
        },
    },
    "required": ["content", "deadline", "participants"],
    "additionalProperties": False,
}

# Schema phang, khong dung oneOf/anyOf: strict function calling bat buoc moi
# property phai nam trong "required", nen field cua nhanh khong dung toi thi
# de nullable thay vi optional.
_REPORT_RESULT_TOOL = {
    "type": "function",
    "name": "report_result",
    "description": "Báo cáo kết quả xử lý input: hoặc là câu trả lời chuyện phiếm, hoặc là JSON giao việc trích xuất được.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["chitchat", "task_extraction"],
                "description": "Loại kết quả: 'chitchat' nếu input là tán gẫu, 'task_extraction' nếu input có nội dung giao việc.",
            },
            "reply": {
                "type": ["string", "null"],
                "description": "Câu trả lời tương tác nếu type='chitchat', null nếu type='task_extraction'.",
            },
            "tasks": {
                "type": ["array", "null"],
                "items": _TASK_ITEM_SCHEMA,
                "description": "Danh sách đầu việc nếu type='task_extraction', null nếu type='chitchat'.",
            },
        },
        "required": ["type", "reply", "tasks"],
        "additionalProperties": False,
    },
}


def run(text: str) -> AssignExtractResult:
    """
    Gui text len LLM, ep tra ve dung 1 trong 2 dang ket qua (chitchat hoac
    task_extraction) qua function calling (strict schema), roi validate lai
    bang pydantic.

    Raises:
        ExtractionFailedError: LLM không gọi function report_result, hoặc
            kết quả trả về không thoả schema.
    """
    client = get_client()

    response = client.responses.create(
        model=get_model(),
        instructions=_SYSPROMPT_TEMPLATE,
        input=text,
        tools=[_REPORT_RESULT_TOOL],
        tool_choice={"type": "function", "name": "report_result"},
    )

    tool_call = next((item for item in response.output if item.type == "function_call"), None)
    if tool_call is None:
        raise ExtractionFailedError("LLM không gọi function report_result trong response.")

    try:
        args = json.loads(tool_call.arguments)
    except json.JSONDecodeError as exc:
        raise ExtractionFailedError(f"Arguments trả về không phải JSON hợp lệ: {exc}") from exc

    result_type = args.get("type")
    try:
        if result_type == "chitchat":
            return ChitChatResult.model_validate(args)
        if result_type == "task_extraction":
            return TaskExtractionResult.model_validate(args)
    except ValidationError as exc:
        raise ExtractionFailedError(f"Kết quả không thoả schema: {exc}") from exc

    raise ExtractionFailedError(f"Giá trị 'type' không hợp lệ: {result_type!r}")
