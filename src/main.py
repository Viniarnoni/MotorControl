import flet as ft
from src.core.database import init_db
from src.ui.views.main_view import MainView

def main(page: ft.Page):
    # Inicializa a View Principal passando a página do Flet
    app_view = MainView(page)
    
    # Adiciona o layout construído à tela
    page.add(app_view.build())
    page.update()

if __name__ == "__main__":
    # 1. Garante que as tabelas do banco existam antes do app abrir
    init_db()
    
    # 2. Inicializa o app desktop nativo
    ft.run(main)
