from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
AIML_DIR = ROOT_DIR / "aiml"
BACKEND_DIR = ROOT_DIR / "apps" / "backend"


def _merge_env_files(filename: str) -> str:
    """
    Gom noi dung file `filename` (".env" hoac ".env.example") tu tat ca
    folder con TRUC TIEP cua aiml/, ghep lai thanh 1 noi dung duy nhat.
    Neu 2 folder cung dinh nghia 1 key, gia tri xuat hien SAU se de len
    gia tri truoc (giong hanh vi cua os.environ khi load nhieu lan).
    """
    blocks: list[str] = []
    seen_keys: dict[str, str] = {}

    for child in sorted(p for p in AIML_DIR.iterdir() if p.is_dir()):
        env_file = child / filename
        if not env_file.exists():
            continue

        for line in env_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key in seen_keys:
                    print(
                        f"  Canh bao: key '{key}' trung giua '{seen_keys[key]}' va "
                        f"'{child.name}' -- gia tri cua '{child.name}' se duoc dung."
                    )
                seen_keys[key] = child.name

        blocks.append(f"# --- tu aiml/{child.name}/{filename} ---")
        blocks.append(env_file.read_text(encoding="utf-8").rstrip())
        blocks.append("")

    return "\n".join(blocks).rstrip() + "\n"


def collect_env_files() -> None:
    """Sinh apps/backend/.env va apps/backend/.env.example tu aiml/*/."""
    BACKEND_DIR.mkdir(parents=True, exist_ok=True)
    for filename in (".env", ".env.example"):
        content = _merge_env_files(filename)
        target = BACKEND_DIR / filename
        target.write_text(content, encoding="utf-8")
        print(f"Da tao {target}")


if __name__ == "__main__":
    collect_env_files()
