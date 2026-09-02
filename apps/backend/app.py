from __future__ import annotations

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# apps/backend tu doc .env cua chinh no (sinh ra tu scripts/collect_env.py),
# doc TRUOC khi import aiml.stt -- de service nay tu chua config, khong
# phu thuoc vao .env nam trong aiml/ luc chay thuc te.
load_dotenv(Path(__file__).resolve().parent / ".env")

# aiml/ va apps/ la 2 thu muc anh em (sibling) o cung goc project -- them
# goc project vao sys.path de import duoc "aiml.stt...." tu day.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from soniox.errors import SonioxAPIError

from aiml.assign_extract import AssignExtractResult, ExtractionFailedError
from aiml.assign_extract import run as assign_extract
from aiml.stt import TranscribeResult, TranscriptionFailedError
from aiml.stt import run as transcribe_audio

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Soniox STT backend")


class AssignExtractRequest(BaseModel):
    text: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/stt/transcribe")
def transcribe(file: UploadFile) -> TranscribeResult:
    """
    Chạy đồng bộ (def, không phải async def) để FastAPI tự đưa request này
    vào threadpool, tránh block event loop trong lúc gọi SDK Soniox (vốn là
    sync) và trong lúc poll chờ kết quả.
    """
    started_at = time.perf_counter()
    try:
        return transcribe_audio(file.file, file.filename)
    except SonioxAPIError as exc:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000)
        raise HTTPException(status_code=502, detail=f"{exc} (sau {elapsed_ms}ms)") from exc
    except TranscriptionFailedError as exc:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000)
        raise HTTPException(status_code=502, detail=f"{exc} (sau {elapsed_ms}ms)") from exc
    except TimeoutError as exc:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000)
        raise HTTPException(status_code=504, detail=f"Transcription timed out (sau {elapsed_ms}ms)") from exc
    except Exception as exc:
        # Fallback cho các lỗi không lường trước (vd httpx.ConnectError, SonioxValidationError...) — đảm bảo client luôn nhận được response có message thay vì "500 Internal Server Error" trắng trơn.
        elapsed_ms = round((time.perf_counter() - started_at) * 1000)
        raise HTTPException(status_code=500, detail=f"Unexpected error (sau {elapsed_ms}ms)") from exc


@app.post("/assign-extract")
def extract(body: AssignExtractRequest) -> AssignExtractResult:
    started_at = time.perf_counter()
    try:
        return assign_extract(body.text)
    except ExtractionFailedError as exc:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000)
        raise HTTPException(status_code=502, detail=f"{exc} (sau {elapsed_ms}ms)") from exc
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000)
        raise HTTPException(status_code=500, detail=f"Unexpected error (sau {elapsed_ms}ms)") from exc


# Mount sau cung, sau tat ca route API o tren -- StaticFiles(html=True) o "/"
# la catch-all, phai dat cuoi de khong nuot mat cac route cu the nhu
# /health, /stt/transcribe, /assign-extract.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
