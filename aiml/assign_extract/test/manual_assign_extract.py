from __future__ import annotations

import argparse
import sys

from aiml.assign_extract import run as assign_extract

sys.stdout.reconfigure(encoding="utf-8")

parser = argparse.ArgumentParser(
    description="Test assign_extract trực tiếp từ terminal, không qua FastAPI."
)
parser.add_argument("text", help="Câu/đoạn văn tự nhiên cần xử lý")
args = parser.parse_args()

result = assign_extract(args.text)

print(result.model_dump_json(indent=2))

# chay tu goc project:
# .venv/Scripts/python.exe -m aiml.assign_extract.test.manual_assign_extract "Chào bạn, hôm nay khoẻ không?"
