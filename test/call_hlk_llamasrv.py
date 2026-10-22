"""
Goi thu LLM tren server Oracle (Ollama + Caddy) qua API chuan OpenAI.

Chay tu goc project:
    .venv/Scripts/python.exe test/call_hlk_llamasrv.py "Xin chao"
    .venv/Scripts/python.exe test/call_hlk_llamasrv.py          # dung prompt mac dinh

Can 3 bien trong .env o goc project: LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

DEFAULT_PROMPT = "Xin chào, giới thiệu ngắn về bạn trong 1 câu."


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    client = OpenAI(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=os.environ["LLM_API_KEY"],
        timeout=300,  # CPU-only ~7 token/s, cau tra loi dai co the mat vai phut
    )
    model = os.environ["LLM_MODEL"]
    prompt = " ".join(sys.argv[1:]) or DEFAULT_PROMPT

    print(f"[{model}] {prompt}\n")
    start = time.perf_counter()
    first_token_at = None
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content if chunk.choices else None
        if text:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            print(text, end="", flush=True)

    end = time.perf_counter()
    ttft = (first_token_at or end) - start
    print(f"\n\n--- token dau tien sau {ttft:.1f}s, tong {end - start:.1f}s")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows mac dinh cp1252, in tieng Viet bi loi
    main()
