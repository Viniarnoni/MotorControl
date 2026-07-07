import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import flet as ft
from src.core.database import init_db
from src.ui.views.dashboard_view import DashboardView
from src.ui.views.motor_view import MotorView
from src.ui.views.cliente_view import ClienteView
from src.ui.views.tabela_preco_view import TabelaPrecoView
from src.ui.views.orcamento_view import OrcamentoView
from src.ui.views.config_view import ConfigView

def main(page: ft.Page):
    init_db()

    page.title = 'OficinaMotor — Gestão de Oficina'
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    conteudo_central = ft.Container(expand=True)

    def mudar_tela(e):
        conteudo_central.content = None 
        
        if e.control.selected_index == 0:
            conteudo_central.content = DashboardView(page).build()
        elif e.control.selected_index == 1:
            conteudo_central.content = MotorView(page).build()
        elif e.control.selected_index == 2:
            conteudo_central.content = ClienteView(page).build()
        elif e.control.selected_index == 3:
            conteudo_central.content = TabelaPrecoView(page)
        elif e.control.selected_index == 4:
            conteudo_central.content = OrcamentoView(page)
            
        page.update()

    sidebar = ft.NavigationRail(
        selected_index=1, 
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        leading=ft.Icon(ft.Icons.BUILD_ROUNDED, color=ft.Colors.BLUE_400, size=32),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_ROUNDED, label='Dashboard'),
            ft.NavigationRailDestination(icon=ft.Icons.ENGINEERING_ROUNDED, label='Motores'),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_ROUNDED, label='Clientes'),
            ft.NavigationRailDestination(icon=ft.Icons.ATTACH_MONEY_ROUNDED, label='Preços'),
            ft.NavigationRailDestination(icon=ft.Icons.REQUEST_QUOTE_ROUNDED, label='Orçamentos'),
        ],
        on_change=mudar_tela
    )
    
    conteudo_central.content = MotorView(page).build()

    page.add(
        ft.Row(
            [sidebar, ft.VerticalDivider(width=1, color=ft.Colors.GREY_800), conteudo_central],
            expand=True
        )
    )

if __name__ == '__main__':
    ft.run(main)
