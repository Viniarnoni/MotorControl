from typing import List
from sqlmodel import select
from src.core.database import get_session
from src.models.entities import Cliente

class ClientRepository:
    @staticmethod
    def create(cliente: Cliente) -> Cliente:
        """Salva um novo cliente no banco de dados."""
        with get_session() as session:
            session.add(cliente)
            session.commit()
            session.refresh(cliente)
            return cliente

    @staticmethod
    def get_all_active() -> List[Cliente]:
        """Retorna todos os clientes ativos (não deletados)."""
        with get_session() as session:
            statement = select(Cliente).where(Cliente.is_active == True)
            return list(session.exec(statement).all())
