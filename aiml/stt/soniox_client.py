from __future__ import annotations

import functools

from dotenv import load_dotenv
from soniox import SonioxClient


@functools.lru_cache(maxsize=1)
def get_client() -> SonioxClient:
    """
    Tao SonioxClient dung 1 lan duy nhat, chi luc thuc su can (khong phai
    luc import module) -- de import module nay khong bat buoc phai co san
    SONIOX_API_KEY trong moi truong.
    """
    load_dotenv()
    return SonioxClient()
