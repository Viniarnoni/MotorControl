from sqlmodel import select
from src.core.database import get_session
from src.models.entities import Orcamento, ItemOrcamento

class OrcamentoRepository:
    @staticmethod
    def create(orcamento: Orcamento, itens: list[ItemOrcamento]):
        with get_session() as session:
            session.add(orcamento)
            session.commit()
            session.refresh(orcamento)
            
            for item in itens:
                item.orcamento_id = orcamento.id
                session.add(item)
                
            session.commit()
            return orcamento

    @staticmethod
    def get_all():
        with get_session() as session:
            return session.exec(select(Orcamento)).all()

    @staticmethod
    def get_itens(orcamento_id: int):
        with get_session() as session:
            return session.exec(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)).all()
