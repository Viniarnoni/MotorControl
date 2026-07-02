import flet as ft
from src.ui.views.dashboard_view import DashboardView
from src.ui.views.motor_view import MotorView
from src.ui.views.cliente_view import ClienteView

def main(page: ft.Page):
    # Configurações globais da janela
    page.title = 'OficinaMotor — Gestão de Oficina'
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # Container que vai segurar o conteúdo da tela selecionada
    conteudo_central = ft.Container(expand=True)

    # Função que escuta o clique no menu e troca as telas
    def mudar_tela(e):
        conteudo_central.content = None # Limpa a tela atual
        
        if e.control.selected_index == 0:
            conteudo_central.content = DashboardView(page).build()
        elif e.control.selected_index == 1:
            conteudo_central.content = MotorView(page).build()
        elif e.control.selected_index == 2:
            conteudo_central.content = ClienteView(page).build()
            
        page.update()

    # Menu lateral (Sidebar)
    sidebar = ft.NavigationRail(
        selected_index=1, # Começa selecionado em 'Motores'
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        leading=ft.Icon(ft.Icons.BUILD_ROUNDED, color=ft.Colors.BLUE_400, size=32),
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_ROUNDED, label='Dashboard'),
            ft.NavigationRailDestination(icon=ft.Icons.ENGINEERING_ROUNDED, label='Motores'),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_ROUNDED, label='Clientes'),
        ],
        on_change=mudar_tela # Aciona a função quando clica
    )
    
    # Injeta a tela inicial na primeira vez que abre o app (Motores)
    conteudo_central.content = MotorView(page).build()

    # Adiciona a estrutura inteira na janela
    page.add(
        ft.Row(
            [sidebar, ft.VerticalDivider(width=1, color=ft.Colors.GREY_800), conteudo_central],
            expand=True
        )
    )

if __name__ == '__main__':
    ft.run(main)
