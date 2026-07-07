import sqlite3
from pathlib import Path

from src.core.database import DATABASE_URL


class ConfigRepository:
    DEFAULTS = {
        "empresa_nome": "ELETRORECUPERADORA",
        "empresa_linha_1": "FELIPE BARRERE ARNONI-MEI CNPJ: 35.032.089/0001-52   Tel:(16) 3252-6033/(16) 98131-5311",
        "empresa_linha_2": "Rua: Ennes Reis Rodrigues, 113 - Jardim Bela Vista - CEP: 15905-004 - Taquaritinga-SP",
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
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL DEFAULT ''
            )
            """
        )
        return conn

    @classmethod
    def _garantir_tabela(cls):
        with cls._connect():
            pass

    @classmethod
    def obter_por_chave(cls, chave: str, padrao: str = "") -> str:
        with cls._connect() as conn:
            row = conn.execute(
                "SELECT valor FROM config WHERE chave = ?",
                (chave,),
            ).fetchone()
        if row and row[0] is not None:
            return row[0]
        return cls.DEFAULTS.get(chave, padrao)

    @classmethod
    def salvar_chave(cls, chave: str, valor: str):
        with cls._connect() as conn:
            conn.execute(
                """
                INSERT INTO config (chave, valor)
                VALUES (?, ?)
                ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor
                """,
                (chave, str(valor or "")),
            )
            conn.commit()

    @classmethod
    def get_company_data(cls) -> dict[str, str]:
        return {
            "empresa_nome": cls.obter_por_chave("empresa_nome", cls.DEFAULTS["empresa_nome"]),
            "empresa_linha_1": cls.obter_por_chave("empresa_linha_1", cls.DEFAULTS["empresa_linha_1"]),
            "empresa_linha_2": cls.obter_por_chave("empresa_linha_2", cls.DEFAULTS["empresa_linha_2"]),
        }
