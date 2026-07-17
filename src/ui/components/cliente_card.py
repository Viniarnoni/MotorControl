import flet as ft

def _formatar_endereco_card(item) -> str:
    partes = []
    if item.endereco:
        rua = item.endereco
        if item.numero:
            rua = f"{rua}, {item.numero}"
        partes.append(rua)
    if item.bairro:
        partes.append(item.bairro)
    if item.cidade:
        cidade = item.cidade
        if item.estado:
            cidade = f"{cidade}/{item.estado}"
        partes.append(cidade)
    elif item.estado:
        partes.append(item.estado)
    return " - ".join(partes) if partes else "Sem endereço"

def criar_card_cliente(item, on_edit, on_delete):
    return ft.Card(
        content=ft.Container(
            padding=15,
            content=ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREEN_400),
                        ft.Text(item.nome, size=16, weight=ft.FontWeight.BOLD),
                    ], spacing=10),
                    ft.Divider(height=5, color=ft.Colors.TRANSPARENT),
                    ft.Row([
                        ft.Icon(ft.Icons.BADGE, color=ft.Colors.GREY_400, size=16),
                        ft.Text(
                            item.gov_id if item.gov_id and item.gov_id.strip() not in ("", "000.000.000-00") else "Sem CNPJ/CPF",
                            color=ft.Colors.GREY,
                            size=13,
                        ),
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.PHONE, color=ft.Colors.GREY_400, size=16),
                        ft.Text(item.telefone if item.telefone else "Sem telefone", color=ft.Colors.GREY, size=13),
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.GREY_400, size=16),
                        ft.Text(_formatar_endereco_card(item), color=ft.Colors.GREY, size=13),
                    ], spacing=5)
                ], expand=True),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.EDIT_ROUNDED, icon_color=ft.Colors.ORANGE_400, tooltip='Editar', on_click=lambda e: on_edit(item)),
                    ft.IconButton(icon=ft.Icons.DELETE_ROUNDED, icon_color=ft.Colors.RED_400, tooltip='Remover', on_click=lambda e: on_delete(item))
                ], alignment=ft.MainAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ), bgcolor=ft.Colors.GREY_900
    )
