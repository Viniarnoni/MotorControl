import sqlite3
from pathlib import Path

from src.core.database import DATABASE_URL


class ConfigRepository:
    DEFAULTS = {
        "empresa_nome": "ELETRORECUPERADORA",
        "empresa_linha_1": "FELIPE BARRERE ARNONI-MEI CNPJ: 35.032.089/0001-52   Tel:(16) 3252-6033/(16) 98131-5311",
        "empresa_linha_2": "Rua: Ennes Reis Rodrigues, 113 - Jardim Bela Vista - CEP:  15905-004 - Taquaritinga-SP",
        "empresa_cnpj": "35.032.089/0001-52",
        "empresa_telefone": "(16) 3252-6033 / (16) 98131-5311",
        "empresa_endereco": "Rua: Ennes Reis Rodrigues, 113 - Jardim Bela Vista",
        "empresa_cep": "15905-004",
        "empresa_cidade_estado": "Taquaritinga-SP",
    }

    @staticmethod
    def _db_path() -> Path:
        database_file = DATABASE_URL.replace("sqlite:///", "", 1)
        path = Path(database_file)
        if path.is_absolute():
            return path
        return Path(__file__).resolve().parents[2] / path

    @classmethod
    def _connect(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(cls._db_path())
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL DEFAULT ''
            )
            """
        )
        return conn

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        with cls._connect() as conn:
            row = conn.execute(
                "SELECT value FROM config WHERE key = ?",
                (key,),
            ).fetchone()
        if row:
            return row[0]
        return cls.DEFAULTS.get(key, default)

    @classmethod
    def set(cls, key: str, value: str) -> None:
        with cls._connect() as conn:
            conn.execute(
                """
                INSERT INTO config (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value or ""),
            )
            conn.commit()

    @classmethod
    def get_company_data(cls) -> dict[str, str]:
        return {key: cls.get(key, default) for key, default in cls.DEFAULTS.items()}

    @classmethod
    def save_company_data(cls, data: dict[str, str]) -> None:
        with cls._connect() as conn:
            for key in cls.DEFAULTS:
                conn.execute(
                    """
                    INSERT INTO config (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    (key, data.get(key, "")),
                )
            conn.commit()
