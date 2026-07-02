from sqlmodel import SQLModel, create_engine, Session
from src.models.entities import Cliente, Motor

DATABASE_URL = "sqlite:///motorcontrol.db"

# engine com eco desativado para produção, mas configurado para SQLite standalone
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    """Cria o banco de dados e as tabelas automaticamente se não existirem."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Gera uma nova sessão de banco de dados para operações."""
    return Session(engine)
