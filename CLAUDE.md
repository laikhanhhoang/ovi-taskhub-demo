# Project notes

## Cấu trúc

- `aiml/` — sân thử nghiệm của team AI (module logic thuần, chưa chắc production-ready)
  - `aiml/stt/` — module STT (Soniox). API công khai qua `aiml/stt/__init__.py` (`run`, `TranscribeResult`, `TranscriptionFailedError`, `Segment`). File có dấu `_` (`_processor.py`, `_schema.py`) là nội bộ, không import trực tiếp từ ngoài `stt/`.
  - `aiml/assign_extract/` — chưa phát triển.
- `apps/backend/` — FastAPI service thực sự chạy. Tự chứa `.env`/`.env.example` riêng (sinh ra từ `apps/scripts/collect_aiml_env_to_backend.py`, không phụ thuộc `.env` trong `aiml/` lúc runtime).
- `apps/frontend/` — chờ `index.html`, chưa có gì.
- `.venv/` ở gốc project — venv **duy nhất, dùng chung** cho cả `aiml/` và `apps/backend/`.

## Chạy

```bash
# Backend (từ gốc project, hoặc cd vào apps/backend rồi bỏ tiền tố)
.venv/Scripts/python.exe apps/backend/app.py

# Test CLI logic stt riêng (không qua FastAPI) — PHẢI chạy từ gốc project
.venv/Scripts/python.exe -m aiml.stt.test.manual_transcribe aiml/stt/test/sounds/sound_giaoviec1.m4a
```

Sau khi sửa/thêm `.env` trong 1 folder con của `aiml/`, chạy lại để đồng bộ sang `apps/backend/`:

```bash
.venv/Scripts/python.exe apps/scripts/collect_aiml_env_to_backend.py
```

## Quy ước

- Hàm chính (entry point) của mỗi `_processor.py` luôn đặt tên `run`.
- Không dùng `utils.py` làm nơi chứa hàm/class lặt vặt — mỗi file nên có 1 mục đích rõ ràng, tự giải thích qua tên file.

## Việc vệ sinh khi làm việc (dành cho Claude)

- `__pycache__` sinh ra khi chạy `python` qua Bash tool **không** bị chặn bởi setting `terminal.integrated.env.windows` trong `.vscode/settings.json` (setting đó chỉ áp dụng cho terminal VSCode tự mở, không áp dụng cho Bash tool). Sau khi test bằng Bash tool, tự dọn:
  ```bash
  find . -iname "__pycache__" -not -path "*/.venv/*" -exec rm -rf {} +
  ```
- Trước khi xoá `.venv/` hoặc bất kỳ folder nào trên Windows, kiểm tra có process nào đang giữ file không (Windows khoá file khi đang mở, khác Linux):
  ```powershell
  Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -like "*<duong-dan-project>*" } | Select-Object ProcessId, ExecutablePath
  ```
  rồi `Stop-Process -Id <id> -Force` trước khi xoá.
- `activate` trong Git Bash của session này không ổn định (thỉnh thoảng trả về Python global thay vì venv) — ưu tiên gọi `python.exe` bằng đường dẫn tuyệt đối/tương đối trực tiếp thay vì `source .venv/Scripts/activate`.
