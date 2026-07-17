import sys
from pathlib import Path

import flet as ft

bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
src_dir = bundle_root / "src"

for candidate in (bundle_root, src_dir):
    candidate_str = str(candidate)
    if candidate.exists() and candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

from src.main import main as app_main


if __name__ == "__main__":
    ft.run(app_main)
