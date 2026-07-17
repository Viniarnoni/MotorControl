from typing import List
from sqlmodel import select
from src.core.database import get_session
from src.models.entities import Cliente

class ClienteRepository:
    
    @staticmethod
    def create(cliente: Cliente) -> Cliente:
        """Salva um novo cliente no banco de dados oficial (motorcontrol.db)."""
        with get_session() as session:
            session.add(cliente)
            session.commit()
            session.refresh(cliente)
            return cliente

    @staticmethod
    def update(cliente: Cliente):
        """Atualiza os dados do cliente."""
        with get_session() as session:
            db_cliente = session.get(Cliente, cliente.id)
            if db_cliente:
                db_cliente.nome = cliente.nome
                db_cliente.telefone = cliente.telefone
                db_cliente.endereco = cliente.endereco
                db_cliente.numero = cliente.numero
                db_cliente.bairro = cliente.bairro
                db_cliente.cidade = cliente.cidade
                db_cliente.estado = cliente.estado
                db_cliente.gov_id = cliente.gov_id
                db_cliente.status = cliente.status
                session.commit()
                session.refresh(db_cliente)
            return db_cliente

    @staticmethod
    def desativar(cliente_id: int):
        """Marca o cliente como inativo em vez de apagar do banco."""
        with get_session() as session:
            db_cliente = session.get(Cliente, cliente_id)
            if db_cliente:
                db_cliente.status = 'Inativo'
                session.commit()

    @staticmethod
    def get_all_active() -> List[Cliente]:
        """Busca todos os clientes ativos ordenados por nome."""
        with get_session() as session:
            statement = select(Cliente).where(Cliente.status == 'Ativo').order_by(Cliente.nome)
            return list(session.exec(statement).all())