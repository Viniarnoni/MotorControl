from sqlmodel import select
from src.core.database import get_session
from src.models.entities import Orcamento, ItemOrcamento
#from src.models.entities import Orcamento, StatusOrcamento

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
        
    @staticmethod
    def contar_por_status():
        try:
            with get_session() as session:
                # Fazemos a busca filtrando diretamente pelo texto do status
                aprovados = len(session.exec(select(Orcamento).where(Orcamento.status == "Aprovado")).all())
                pendentes = len(session.exec(select(Orcamento).where(Orcamento.status == "Pendente")).all())
                reprovados = len(session.exec(select(Orcamento).where(Orcamento.status == "Reprovado")).all())
                
                return aprovados, pendentes, reprovados
        except Exception as e:
            print(f"Erro ao contar status: {e}")
            return 0, 0, 0
