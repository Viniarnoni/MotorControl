from typing import List
from sqlmodel import select
from src.core.database import get_session
from src.models.entities import Motor

class MotorRepository:
    @staticmethod
    def create(motor: Motor) -> Motor:
        """Salva um novo motor no banco de dados associado a um cliente."""
        with get_session() as session:
            session.add(motor)
            session.commit()
            session.refresh(motor)
            return motor

    @staticmethod
    def get_all_active() -> List[Motor]:
        """Retorna todos os motores ativos com os dados dos clientes carregados."""
        with get_session() as session:
            # O SQLModel resolve o relacionamento automaticamente ao acessar .cliente
            statement = select(Motor).where(Motor.is_active == True)
            return list(session.exec(statement).all())
