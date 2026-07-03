import flet as ft
from src.repositories.orcamento_repo import OrcamentoRepository

class DashboardView:
    def __init__(self, page: ft.Page):
        self.page = page

        aprovados, pendentes, reprovados = OrcamentoRepository.contar_por_status()
        
        self.qtd_aprovados = aprovados
        self.qtd_pendentes = pendentes
        self.qtd_reprovados = reprovados
        
    def _criar_card(self, titulo: str, valor: int, icone: str, cor: str):
        """Função auxiliar para padronizar o visual dos cards"""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icone, color=cor, size=28), 
                            ft.Text(titulo, size=16, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_300)
                        ], 
                        alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Text(str(valor), size=38, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                ],
                spacing=5,
            ),
            padding=20,
            bgcolor=ft.Colors.GREY_900,
            border_radius=12,
            width=260,
        )

    def build(self):
        linha_de_cards = ft.Row(
            controls=[
                self._criar_card("Aprovados", self.qtd_aprovados, ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, ft.Colors.GREEN_400),
                self._criar_card("Pendentes", self.qtd_pendentes, ft.Icons.HOURGLASS_EMPTY_ROUNDED, ft.Colors.AMBER_400),
                self._criar_card("Reprovados", self.qtd_reprovados, ft.Icons.CANCEL_OUTLINED, ft.Colors.RED_400),
            ],
            wrap=True,
            spacing=20
        )

        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Text('Dashboard Principal', size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=ft.Colors.GREY_800),
                
                linha_de_cards,
                
                ft.Container(height=40),
                ft.Text('Gráficos e estatísticas em desenvolvimento...', color=ft.Colors.GREY_500)
            ])
        )
    
    @staticmethod
    def contar_por_status():
        with Session(engine) as session:
            aprovados = session.query(Orcamento).filter(Orcamento.status == "Aprovado").count()
            pendentes = session.query(Orcamento).filter(Orcamento.status == "Pendente").count()
            reprovados = session.query(Orcamento).filter(Orcamento.status == "Reprovado").count()
            return aprovados, pendentes, reprovados
        
           
