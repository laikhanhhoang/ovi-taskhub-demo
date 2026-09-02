from __future__ import annotations

import argparse
import os
import sys

from aiml.stt import run as transcribe_audio

sys.stdout.reconfigure(encoding="utf-8")

parser = argparse.ArgumentParser(
    description="Test transcribe_audio trực tiếp từ terminal, không qua FastAPI."
)
parser.add_argument("audio_path", help="Đường dẫn tới file audio cần transcribe")
args = parser.parse_args()

with open(args.audio_path, "rb") as f:
    result = transcribe_audio(f, filename=os.path.basename(args.audio_path))

print(result.model_dump_json(indent=2))

# chay tu goc project: python -m aiml.stt.test.manual_transcribe aiml/stt/test/sounds/sound_giaoviec1.m4a
