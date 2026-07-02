from sqlmodel import select
from src.core.database import get_session
from src.models.entities import PrecoPeca

class PrecoPecaRepository:
    @staticmethod
    def create(peca: PrecoPeca):
        with get_session() as session:
            session.add(peca)
            session.commit()
            session.refresh(peca)
            return peca

    @staticmethod
    def get_all():
        with get_session() as session:
            return session.exec(select(PrecoPeca)).all()

    @staticmethod
    def delete(peca_id: int):
        with get_session() as session:
            peca = session.get(PrecoPeca, peca_id)
            if peca:
                session.delete(peca)
                session.commit()
