from __future__ import annotations

import functools
import os

from dotenv import load_dotenv
from openai import OpenAI


@functools.lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """
    Tao OpenAI client dung 1 lan duy nhat, chi luc thuc su can (khong phai
    luc import module) -- de import module nay khong bat buoc phai co san
    ASSIGN_EXTRACT_API_KEY trong moi truong.
    """
    load_dotenv()
    return OpenAI(
        api_key=os.environ["ASSIGN_EXTRACT_API_KEY"],
        base_url=os.environ["ASSIGN_EXTRACT_BASE_URL"],
    )


def get_model() -> str:
    load_dotenv()
    return os.environ["ASSIGN_EXTRACT_MODEL"]
