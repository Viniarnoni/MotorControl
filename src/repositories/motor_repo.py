from typing import List
from sqlmodel import select
from sqlalchemy import or_
from src.core.database import get_session
from src.models.entities import Motor, Orcamento

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
    def buscar_para_rastreabilidade(termo: str = "") -> List[Motor]:
        """Busca motores por tipo, marca, modelo ou nome do cliente para análise histórica."""
        with get_session() as session:
            statement = select(Motor).order_by(Motor.cliente, Motor.marca, Motor.tipo)

            if termo:
                termo_like = f"%{termo.strip()}%"
                statement = statement.where(
                    or_(
                        Motor.tipo.ilike(termo_like),
                        Motor.marca.ilike(termo_like),
                        Motor.modelo.ilike(termo_like),
                        Motor.cliente.ilike(termo_like),
                    )
                )

            return list(session.exec(statement).all())

    @staticmethod
    def obter_historico_por_motor(motor_id: int) -> list[dict]:
        """Retorna a linha do tempo de orçamentos vinculados ao motor."""
        with get_session() as session:
            statement = (
                select(Orcamento, Motor)
                .join(Motor, Motor.id == Orcamento.motor_id)
                .where(Orcamento.motor_id == motor_id)
                .order_by(Orcamento.data_emissao.desc(), Orcamento.id.desc())
            )

            historico = []
            for orcamento, motor in session.exec(statement).all():
                descricao_servico = (
                    orcamento.descricao_mao_de_obra
                    or motor.problema_relatado
                    or "Não informado"
                )
                historico.append(
                    {
                        "orcamento_id": orcamento.id,
                        "data_entrada": orcamento.data_emissao,
                        "problema_ou_servico": descricao_servico,
                        "valor_total": orcamento.valor_total or 0.0,
                        "status": orcamento.status or "Pendente",
                    }
                )

            return historico
            
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
