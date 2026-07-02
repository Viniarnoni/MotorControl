import flet as ft

class DashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        
    def build(self):
        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Text('Dashboard Principal', size=28, weight=ft.FontWeight.BOLD),
                ft.Divider(height=20, color=ft.Colors.GREY_800),
                ft.Text('Gráficos e estatísticas em desenvolvimento...', color=ft.Colors.GREY_400)
            ])
        )
