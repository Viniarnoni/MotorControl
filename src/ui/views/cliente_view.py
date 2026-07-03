import flet as ft
from src.repositories.cliente_repo import ClienteRepository
from src.ui.components.cliente_form import ClienteFormModal
from src.ui.components.cliente_card import criar_card_cliente

class ClienteView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.form_modal = ClienteFormModal(page, on_success=self.atualizar_lista_tela)
        
        self.txt_busca = ft.TextField(
            hint_text="Buscar cliente por nome... ",
            prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.GREEN_700, expand=True,
            on_change=lambda e: self.atualizar_lista_tela()
        )
        
        self.lista_vazia = ft.Text('Nenhum cliente cadastrado...', color=ft.Colors.GREY_400)
        self.coluna_listagem = ft.Column([self.lista_vazia], spacing=10)
        
        self.cliente_para_excluir = None
        self.modal_exclusao = ft.AlertDialog(
            title=ft.Text('Confirmar Exclusão'),
            content=ft.Text('Deseja realmente remover este cliente?'),
            actions=[
                ft.TextButton('Cancelar', on_click=lambda e: self.fechar_modal_exclusao()),
                ft.Button('Excluir', bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=self.confirmar_exclusao)
            ]
        )

    def abrir_novo_cliente(self, e):
        self.form_modal.abrir_para_novo()

    def editar_cliente(self, cliente):
        self.form_modal.abrir_para_editar(cliente)

    def abrir_excluir_cliente(self, cliente):
        self.cliente_para_excluir = cliente
        if self.modal_exclusao not in self.page.overlay:
            self.page.overlay.append(self.modal_exclusao)
        self.modal_exclusao.open = True
        self.page.update()

    def fechar_modal_exclusao(self):
        self.modal_exclusao.open = False
        self.page.update()

    def confirmar_exclusao(self, e):
        if self.cliente_para_excluir:
            ClienteRepository.desativar(self.cliente_para_excluir.id)
            self.fechar_modal_exclusao()
            self.atualizar_lista_tela()
            self.page.snack_bar = ft.SnackBar(ft.Text('Cliente removido!'), bgcolor=ft.Colors.RED_700)
            self.page.snack_bar.open = True
            self.page.update()

    def atualizar_lista_tela(self):
        lista = ClienteRepository.get_all_active()
        termo = self.txt_busca.value.lower() if self.txt_busca.value else ""
        
        if termo:
            lista = [c for c in lista if termo in (c.nome or "").lower()]
            
        self.coluna_listagem.controls.clear()
        if lista:
            for item in lista:
                card = criar_card_cliente(
                    item=item,
                    on_edit=self.editar_cliente,
                    on_delete=self.abrir_excluir_cliente
                )
                self.coluna_listagem.controls.append(card)
        else:
            self.coluna_listagem.controls.append(
                ft.Text('Nenhum cliente corresponde à busca.', color=ft.Colors.GREY_400, italic=True) if termo else self.lista_vazia
            )
        self.page.update()
            
    def build(self):
        self.atualizar_lista_tela()
        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Row([
                    ft.Text('Gerenciamento de Clientes', size=28, weight=ft.FontWeight.BOLD),
                    ft.Button('Novo Cliente', icon=ft.Icons.PERSON_ADD, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, on_click=self.abrir_novo_cliente)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([self.txt_busca], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=15, color=ft.Colors.GREY_800),
                self.coluna_listagem
            ], scroll=ft.ScrollMode.ALWAYS)
        )
