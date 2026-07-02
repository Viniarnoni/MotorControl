from sqlmodel import select
from src.core.database import get_session
from src.models.entities import PrecoServico

class PrecoServicoRepository:
    @staticmethod
    def create(preco: PrecoServico):
        with get_session() as session:
            session.add(preco)
            session.commit()
            session.refresh(preco)
            return preco

    @staticmethod
    def get_all():
        with get_session() as session:
            return session.exec(select(PrecoServico)).all()

    @staticmethod
    def buscar_por_matriz(cv: str, fases: str, polos: str):
        with get_session() as session:
            statement = select(PrecoServico).where(
                PrecoServico.cv == cv,
                PrecoServico.fases == fases,
                PrecoServico.polos == polos
            )
            return session.exec(statement).first()

    @staticmethod
    def delete(preco_id: int):
        with get_session() as session:
            preco = session.get(PrecoServico, preco_id)
            if preco:
                session.delete(preco)
                session.commit()
