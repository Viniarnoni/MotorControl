import sys
from pathlib import Path


def get_app_root() -> Path:
    """Retorna a pasta base do app em dev e no executável."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def get_database_path() -> Path:
    """Banco persistente ao lado do projeto em dev e ao lado do .exe em produção."""
    return get_app_root() / "motorcontrol.db"


def get_backups_dir() -> Path:
    return get_app_root() / "backups"


def get_logo_path() -> Path | None:
    """Logo da empresa para PDF: pasta assets ao lado do app ou embutida no exe."""
    candidatos = [get_app_root() / "assets" / "logo.png"]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidatos.append(Path(meipass) / "assets" / "logo.png")
    for caminho in candidatos:
        if caminho.exists():
            return caminho
    return None

