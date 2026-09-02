from __future__ import annotations

import sys
from pathlib import Path

import yaml

from aiml.assign_extract import run as assign_extract

sys.stdout.reconfigure(encoding="utf-8")

TEST_DIR = Path(__file__).parent
input_path = TEST_DIR / "input.yaml"
output_path = TEST_DIR / "output.yaml"

cases = yaml.safe_load(input_path.read_text(encoding="utf-8")) or []

results = []
for case in cases:
    result = assign_extract(case["text"])
    results.append({"input": case, "output": result.model_dump(mode="json")})
    print(f"Đã xử lý: {case['text'][:50]!r}")

output_path.write_text(
    yaml.dump(results, allow_unicode=True, sort_keys=False, default_flow_style=False),
    encoding="utf-8",
)
print(f"Đã ghi {len(results)} kết quả vào {output_path}")

# chay tu goc project:
# .venv/Scripts/python.exe -m aiml.assign_extract.test.manual_batch_test
