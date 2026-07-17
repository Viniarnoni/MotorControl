from sqlmodel import SQLModel, create_engine, Session
from src.models.entities import Cliente, Motor
from src.core.paths import get_database_path

DATABASE_PATH = get_database_path()
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# engine com eco desativado para produção, mas configurado para SQLite standalone
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    """Cria o banco de dados e as tabelas automaticamente se não existirem."""
    SQLModel.metadata.create_all(engine)
    from src.migration import migrate_db
    migrate_db()

def get_session():
    """Gera uma nova sessão de banco de dados para operações."""
    return Session(engine)
