import flet as ft
import os
from src.repositories.motor_repo import MotorRepository
from src.ui.components.motor_card import criar_card_motor
from src.ui.components.motor_form import MotorFormModal

class MotorView:
    def __init__(self, page: ft.Page):
        self.page = page
        
        # O formulário agora mora no arquivo dele e a gente só chama ele aqui
        self.form_modal = MotorFormModal(page, on_success=self.atualizar_lista_tela)
        
        self.txt_busca = ft.TextField(
            hint_text="Buscar por equipamento, marca, modelo ou nº de série...",
            prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.BLUE_700, expand=True,
            on_change=lambda e: self.atualizar_lista_tela()
        )
        
        self.lista_vazia = ft.Text('Nenhum motor encontrado...', color=ft.Colors.GREY_400)
        self.coluna_listagem = ft.Column([self.lista_vazia], spacing=10)
        
        self.motor_para_excluir = None
        self.modal_exclusao = ft.AlertDialog(
            title=ft.Text('Confirmar Exclusão'),
            content=ft.Text('Tem a certeza de que deseja remover este equipamento?'),
            actions=[
                ft.TextButton('Cancelar', on_click=self.fechar_modal_exclusao),
                ft.ElevatedButton('Excluir', bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=self.confirmar_exclusao)
            ]
        )
        
        self.img_foto_ampliada = ft.Image(src="", fit="contain", height=400)
        self.modal_ver_foto = ft.AlertDialog(
            title=ft.Text('Visualizar Foto'),
            content=ft.Container(content=self.img_foto_ampliada, width=500, height=400),
            actions=[ft.TextButton('Fechar', on_click=lambda e: self.fechar_modal_foto())],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def abrir_novo_motor(self, e):
        self.form_modal.abrir_para_novo()

    def editar_motor(self, motor):
        self.form_modal.abrir_para_editar(motor)

    def abrir_excluir_motor(self, motor):
        self.motor_para_excluir = motor
        if self.modal_exclusao not in self.page.overlay:
            self.page.overlay.append(self.modal_exclusao)
        self.modal_exclusao.open = True
        self.page.update()

    def fechar_modal_exclusao(self, e=None):
        self.modal_exclusao.open = False
        self.page.update()

    def confirmar_exclusao(self, e):
        if self.motor_para_excluir:
            MotorRepository.desativar(self.motor_para_excluir.id)
            self.fechar_modal_exclusao()
            self.atualizar_lista_tela()
            self.page.snack_bar = ft.SnackBar(ft.Text('Equipamento arquivado!'), bgcolor=ft.Colors.RED_700)
            self.page.snack_bar.open = True
            self.page.update()

    def visualizar_foto(self, caminho):
        if caminho and os.path.exists(caminho):
            self.img_foto_ampliada.src = os.path.abspath(caminho)
            if self.modal_ver_foto not in self.page.overlay:
                self.page.overlay.append(self.modal_ver_foto)
            self.modal_ver_foto.open = True
            self.page.update()

    def fechar_modal_foto(self):
        self.modal_ver_foto.open = False
        self.page.update()

    def atualizar_lista_tela(self):
        lista = MotorRepository.get_all_active()
        termo = self.txt_busca.value.lower() if self.txt_busca.value else ""
        
        if termo:
            lista = [
                i for i in lista if
                termo in (i.tipo or "").lower() or
                termo in (i.marca or "").lower() or
                termo in (i.modelo or "").lower() or
                termo in (i.numero_serie or "").lower()
            ]
            
        self.coluna_listagem.controls.clear()
        if lista:
            for item in lista:
                # Chama a função que desenha o card importada do nosso componente
                card = criar_card_motor(
                    item=item, 
                    on_edit=self.editar_motor, 
                    on_delete=self.abrir_excluir_motor, 
                    on_view_photo=self.visualizar_foto
                )
                self.coluna_listagem.controls.append(card)
        else:
            self.coluna_listagem.controls.append(
                ft.Text('Nenhum equipamento corresponde à busca.', color=ft.Colors.GREY_400, italic=True) if termo else self.lista_vazia
            )
        self.page.update()
            
    def build(self):
        self.atualizar_lista_tela()
        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Row([
                    ft.Text('Motores e Equipamentos', size=28, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton('Novo motor', icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.abrir_novo_motor)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([self.txt_busca], alignment=ft.MainAxisAlignment.START),
                ft.Divider(height=15, color=ft.Colors.GREY_800),
                self.coluna_listagem
            ], scroll=ft.ScrollMode.ALWAYS)
        )
