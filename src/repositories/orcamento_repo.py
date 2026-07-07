from sqlmodel import select, func
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
                aprovados = len(session.exec(select(Orcamento).where(Orcamento.status == "Aprovado")).all())
                pendentes = len(session.exec(select(Orcamento).where(Orcamento.status == "Pendente")).all())
                reprovados = len(session.exec(select(Orcamento).where(Orcamento.status == "Reprovado")).all())
                finalizados = len(session.exec(select(Orcamento).where(Orcamento.status == "Finalizado")).all())
                
                return aprovados, pendentes, reprovados, finalizados
        except Exception as e:
            print(f"Erro ao contar status: {e}")
            return 0, 0, 0, 0

    @staticmethod
    def obter_resumo_financeiro():
        try:
            with get_session() as session:
                orcamentos = session.exec(select(Orcamento)).all()
                total_orcamentos = len(orcamentos)
                faturamento_estimado = sum((o.valor_total or 0.0) for o in orcamentos)
                ticket_medio = (
                    faturamento_estimado / total_orcamentos
                    if total_orcamentos > 0
                    else 0.0
                )

                return {
                    "total_orcamentos": total_orcamentos,
                    "faturamento_estimado": faturamento_estimado,
                    "ticket_medio": ticket_medio,
                }
        except Exception as e:
            print(f"Erro ao obter resumo financeiro: {e}")
            return {
                "total_orcamentos": 0,
                "faturamento_estimado": 0.0,
                "ticket_medio": 0.0,
            }

    @staticmethod
    def obter_ultimos_orcamentos(limit: int = 5):
        try:
            with get_session() as session:
                statement = select(Orcamento).order_by(Orcamento.id.desc()).limit(limit)
                return list(session.exec(statement).all())
        except Exception as e:
            print(f"Erro ao obter últimos orçamentos: {e}")
            return []

    @staticmethod
    def obter_funil_status():
        try:
            with get_session() as session:
                statement = (
                    select(Orcamento.status, func.count(Orcamento.id))
                    .group_by(Orcamento.status)
                )
                rows = session.exec(statement).all()

                funil = {
                    "Pendente": 0,
                    "Aprovado": 0,
                    "Finalizado": 0,
                    "Recusado": 0,
                }

                for status, quantidade in rows:
                    if status == "Reprovado":
                        funil["Recusado"] += quantidade
                    elif status in funil:
                        funil[status] += quantidade

                return funil
        except Exception as e:
            print(f"Erro ao obter funil por status: {e}")
            return {
                "Pendente": 0,
                "Aprovado": 0,
                "Finalizado": 0,
                "Recusado": 0,
            }
