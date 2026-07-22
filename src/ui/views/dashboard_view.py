import flet as ft
from src.repositories.orcamento_repo import OrcamentoRepository

class DashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.resumo = OrcamentoRepository.obter_resumo_financeiro()
        self.funil_status = OrcamentoRepository.obter_funil_status()
        self.ultimos_orcamentos = OrcamentoRepository.obter_ultimos_orcamentos(limit=5)

    def _formatar_moeda(self, valor: float) -> str:
        return f"R$ {(valor or 0.0):.2f}"

    def _criar_card(self, titulo: str, valor: str, icone: str, cor: str):
        return ft.Card(
            elevation=2,
            content=ft.Container(
                width=320,
                height=120,
                padding=20,
                bgcolor=ft.Colors.GREY_900,
                border_radius=12,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icone, color=cor, size=24),
                                ft.Text(
                                    titulo,
                                    size=15,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.GREY_300,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Text(valor, size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ),
        )

    def _criar_linha_orcamento(self, orcamento):
        return ft.Card(
            elevation=1,
            content=ft.Container(
                padding=12,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    orcamento.cliente_nome or "Cliente não informado",
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                    size=15,
                                ),
                                ft.Text(
                                    orcamento.motor_descricao or "Sem descrição do motor",
                                    color=ft.Colors.GREY_400,
                                    size=12,
                                ),
                            ],
                            spacing=2,
                            width=700,
                        ),
                        ft.Text(
                            self._formatar_moeda(orcamento.valor_total),
                            color=ft.Colors.GREEN_400,
                            weight=ft.FontWeight.BOLD,
                            size=15,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
        )

    def _criar_mini_card_status(self, titulo: str, quantidade: int, icone: str, cor: str):
        return ft.Card(
            elevation=1,
            content=ft.Container(
                width=235,
                padding=15,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icone, color=cor, size=20),
                                ft.Text(titulo, color=cor, weight=ft.FontWeight.BOLD, size=14),
                            ],
                            spacing=8,
                        ),
                        ft.Text(str(quantidade), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ],
                    spacing=8,
                ),
            ),
        )

    def build(self):
        cards_resumo = ft.Row(
            [
                self._criar_card(
                    "Total de Orçamentos",
                    str(self.resumo["total_orcamentos"]),
                    ft.Icons.RECEIPT_LONG,
                    ft.Colors.BLUE_400,
                ),
                self._criar_card(
                    "Faturamento Estimado",
                    f"R$ {self.resumo['faturamento_estimado']:.2f}",
                    ft.Icons.ATTACH_MONEY,
                    ft.Colors.GREEN_400,
                ),
                self._criar_card(
                    "Ticket Médio",
                    f"R$ {self.resumo['ticket_medio']:.2f}",
                    ft.Icons.INSIGHTS,
                    ft.Colors.AMBER_400,
                ),
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        )

        mini_cards_status = ft.Row(
            [
                self._criar_mini_card_status(
                    "Pendente",
                    self.funil_status["Pendente"],
                    ft.Icons.HOURGLASS_EMPTY,
                    ft.Colors.AMBER_400,
                ),
                self._criar_mini_card_status(
                    "Aprovado",
                    self.funil_status["Aprovado"],
                    ft.Icons.CHECK_CIRCLE_OUTLINE,
                    ft.Colors.GREEN_400,
                ),
                self._criar_mini_card_status(
                    "Finalizado",
                    self.funil_status["Finalizado"],
                    ft.Icons.DONE_ALL,
                    ft.Colors.BLUE_400,
                ),
                self._criar_mini_card_status(
                    "Recusado",
                    self.funil_status["Recusado"],
                    ft.Icons.CANCEL_OUTLINED,
                    ft.Colors.RED_400,
                ),
            ],
            spacing=15,
            alignment=ft.MainAxisAlignment.START,
        )

        lista_ultimos = (
            [self._criar_linha_orcamento(orcamento) for orcamento in self.ultimos_orcamentos]
            if self.ultimos_orcamentos
            else [
                ft.Container(
                    padding=20,
                    border_radius=10,
                    bgcolor=ft.Colors.GREY_900,
                    content=ft.Text(
                        "Nenhum orçamento emitido até o momento.",
                        color=ft.Colors.GREY_400,
                        italic=True,
                    ),
                )
            ]
        )

        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Text('Dashboard Principal', size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=ft.Colors.GREY_800),
                cards_resumo,
                ft.Container(height=20),
                mini_cards_status,
                ft.Container(height=30),
                ft.Text('Últimos 5 Orçamentos Emitidos', size=20, weight=ft.FontWeight.BOLD),
                ft.Text(
                    'Resumo recente com cliente e valor total de cada orçamento.',
                    color=ft.Colors.GREY_400,
                ),
                ft.Container(height=10),
                ft.Column(lista_ultimos, spacing=10),
            ], scroll=ft.ScrollMode.AUTO)
        )
