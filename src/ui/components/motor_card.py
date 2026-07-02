import flet as ft
from datetime import datetime

def criar_card_motor(item, on_edit, on_delete, on_view_photo):
    prob = item.problema_relatado if item.problema_relatado else 'Não informado'
    
    dt_exibicao = ""
    if item.data_entrada:
        if isinstance(item.data_entrada, str):
            try:
                dt_exibicao = datetime.strptime(item.data_entrada.split(" ")[0], "%Y-%m-%d").strftime("%d/%m/%Y")
            except:
                dt_exibicao = item.data_entrada
        else:
            dt_exibicao = item.data_entrada.strftime("%d/%m/%Y")
    
    icone_foto = ft.IconButton(
        icon=ft.Icons.IMAGE, 
        icon_color=ft.Colors.GREEN_400, 
        icon_size=20,
        tooltip="Clique para ver a foto do motor",
        on_click=lambda e: on_view_photo(item.caminho_foto)
    ) if item.caminho_foto else ft.Container()
    
    return ft.Card(
        content=ft.Container(
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Text(f'{item.tipo} - {item.marca} {item.modelo}', size=16, weight=ft.FontWeight.BOLD),
                            ft.Container(ft.Text(item.status, size=11), bgcolor=ft.Colors.BLUE_900, padding=5, border_radius=5),
                            icone_foto
                        ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Text(f'Dados Técnicos: {item.cv} CV | {item.rpm} RPM | {item.tensao}V', color=ft.Colors.GREY_400, size=13),
                        ft.Text(f'Data de Entrada: {dt_exibicao}', color=ft.Colors.BLUE_300, size=13),
                        ft.Text(f'Nº Série: {item.numero_serie if item.numero_serie else "Não informado"}', color=ft.Colors.GREY_500, size=12),
                        ft.Text(f'Problema: {prob}', color=ft.Colors.RED_300, size=12)
                    ], expand=True),
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT_ROUNDED, icon_color=ft.Colors.ORANGE_400, tooltip='Editar', on_click=lambda e: on_edit(item)),
                        ft.IconButton(icon=ft.Icons.DELETE_ROUNDED, icon_color=ft.Colors.RED_400, tooltip='Remover', on_click=lambda e: on_delete(item))
                    ], alignment=ft.MainAxisAlignment.END)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=5)
        ), bgcolor=ft.Colors.GREY_900
    )
