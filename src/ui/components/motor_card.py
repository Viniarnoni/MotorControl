import flet as ft
from src.models.entities import Motor

def criar_card_motor(item: Motor, on_delete=None, on_edit=None, on_view_photo=None, *args, **kwargs):
    # Passamos item.caminho_foto para a função não quebrar com o tipo 'Motor'
    return ft.Card(
        content=ft.Container(
            padding=15,
            content=ft.Column([
                # Linha Superior: Ícone, Título e Status
                ft.Row([
                    ft.Icon(ft.Icons.ENGINEERING, color=ft.Colors.BLUE_400, size=30),
                    ft.Column([
                        ft.Text(f"{item.marca} - {item.modelo or item.tipo}", size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Cliente: {item.cliente}", size=13, color=ft.Colors.GREY_400),
                    ], spacing=2, expand=True),
                    ft.Container(
                        content=ft.Text("Ativo" if item.is_active else "Finalizado", size=11), 
                        bgcolor=ft.Colors.BLUE_900 if item.is_active else ft.Colors.GREY_700, 
                        padding=5, 
                        border_radius=5
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=1, color=ft.Colors.GREY_800),
                
                # Bloco de Informações Técnicas Reais da Entidade
                ft.Row([
                    ft.Column([
                        ft.Text(f"Potência: {item.cv if item.cv else 'N/I'}", color=ft.Colors.GREY_400, size=12),
                        ft.Text(f"RPM: {item.rpm if item.rpm else 'N/I'}", color=ft.Colors.GREY_400, size=12),
                    ], expand=True),
                    ft.Column([
                        ft.Text(f"Tensão: {item.tensao if item.tensao else 'N/I'}", color=ft.Colors.GREY_400, size=12),
                        ft.Text(f"Rede/Fases: {item.fases if item.fases else 'N/I'}", color=ft.Colors.GREY_400, size=12),
                    ], expand=True),
                    ft.Column([
                        ft.Text(f"Polos: {item.polos if item.polos else 'N/I'}", color=ft.Colors.GREY_400, size=12),
                    ], expand=True),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Linha de Detalhes Adicionais (Problema e Data)
                ft.Row([
                    ft.Text(
                        f"Problema: {item.problema_relatado if item.problema_relatado else 'Não informado'}", 
                        color=ft.Colors.ORANGE_300, 
                        size=12, 
                        italic=True,
                        expand=True
                    ),
                    ft.Text(
                        f"Entrada: {item.data_entrada.strftime('%d/%m/%Y') if item.data_entrada else ''}", 
                        color=ft.Colors.GREY_500, 
                        size=11
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=1, color=ft.Colors.GREY_800),
                
                # Botões de Ação
                ft.Row([
                    ft.IconButton(
                        ft.Icons.IMAGE, 
                        icon_color=ft.Colors.GREEN_400, 
                        tooltip="Visualizar Foto",
                        on_click=lambda e: on_view_photo(item.caminho_foto) if on_view_photo else None
                    ),
                    ft.IconButton(
                        ft.Icons.EDIT, 
                        icon_color=ft.Colors.BLUE_400, 
                        tooltip="Editar Motor",
                        on_click=lambda e: on_edit(item) if on_edit else None
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE, 
                        icon_color=ft.Colors.RED_400, 
                        tooltip="Excluir Motor",
                        on_click=lambda e: on_delete(item) if on_delete else None
                    ),
                ], alignment=ft.MainAxisAlignment.END, spacing=5)
            ], spacing=10)
        ),
        margin=10
    )
