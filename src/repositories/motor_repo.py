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
    def update(motor: Motor) -> Motor:
        """Atualiza os dados de um motor que já existe no banco."""
        with get_session() as session:
            session.add(motor) # No SQLModel, o add() atualiza se o objeto já tiver um ID
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
            
    @staticmethod
    def desativar(motor_id: int) -> bool:
        """Faz o 'soft delete', alterando o is_active para False (vai para o Histórico)."""
        with get_session() as session:
            motor = session.get(Motor, motor_id)
            if motor:
                motor.is_active = False
                session.add(motor)
                session.commit()
                return True
            return False