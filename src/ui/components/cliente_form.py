import flet as ft
import re
from src.models.cliente_entity import Cliente
from src.repositories.cliente_repo import ClienteRepository

class ClienteFormModal:
    def __init__(self, page: ft.Page, on_success):
        self.page = page
        self.on_success = on_success
        self.cliente_em_edicao = None
        
        self.txt_nome = ft.TextField(label='Nome Completo / Razão Social *', border_color=ft.Colors.GREY_700)
        
        # Filtro simplificado: Aceita APENAS números puros e limita a 11 dígitos
        self.txt_telefone = ft.TextField(
            label='Telefone / WhatsApp (Apenas números)', 
            hint_text='Ex: 11999999999', 
            border_color=ft.Colors.GREY_700,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=11
        )
        
        self.txt_endereco = ft.TextField(label='Endereço (Opcional)', border_color=ft.Colors.GREY_700, multiline=True, min_lines=2)
        self.btn_salvar = ft.ElevatedButton('Salvar Cliente', bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_cliente)
        
        self.modal = ft.AlertDialog(
            title=ft.Text('Cadastrar Novo Cliente', weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=450, height=320,
                content=ft.Column([
                    self.txt_nome,
                    self.txt_telefone,
                    self.txt_endereco
                ], spacing=15)
            ),
            actions=[
                ft.TextButton('Cancelar', on_click=lambda e: self.fechar_modal()),
                self.btn_salvar
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def formatar_telefone(self, num_puro):
        """Formata string de números puros para o padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"""
        if not num_puro:
            return ""
        # Remove qualquer resíduo que não seja número
        num = re.sub(r"\D", "", num_puro)
        
        if len(num) == 11: # Celular com 9 dígitos
            return f"({num[0:2]}) {num[2:7]}-{num[7:]}"
        elif len(num) == 10: # Fixo com 8 dígitos
            return f"({num[0:2]}) {num[2:6]}-{num[6:]}"
        return num # Se tiver menos dígitos, salva o que foi digitado

    def abrir_para_novo(self):
        self.cliente_em_edicao = None
        self.modal.title.value = 'Cadastrar Novo Cliente'
        self.btn_salvar.text = 'Salvar Cliente'
        self.btn_salvar.bgcolor = ft.Colors.BLUE_700
        self.txt_nome.value = ""
        self.txt_telefone.value = ""
        self.txt_endereco.value = ""
        self.abrir_modal()

    def abrir_para_editar(self, cliente):
        self.cliente_em_edicao = cliente
        self.modal.title.value = 'Editar Cliente'
        self.btn_salvar.text = 'Salvar Alterações'
        self.btn_salvar.bgcolor = ft.Colors.ORANGE_700
        self.txt_nome.value = cliente.nome
        
        # Ao editar, removemos a formatação pro usuário alterar apenas os números
        self.txt_telefone.value = re.sub(r"\D", "", cliente.telefone or "")
        self.txt_endereco.value = cliente.endereco
        self.abrir_modal()

    def abrir_modal(self):
        if self.modal not in self.page.overlay:
            self.page.overlay.append(self.modal)
        self.modal.open = True
        self.page.update()

    def fechar_modal(self):
        self.modal.open = False
        self.page.update()

    def salvar_cliente(self, e):
        if not self.txt_nome.value:
            self.page.snack_bar = ft.SnackBar(ft.Text('O nome do cliente é obrigatório!'), bgcolor=ft.Colors.ORANGE_800)
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        # Formata o telefone antes de mandar pro banco
        telefone_formatado = self.formatar_telefone(self.txt_telefone.value)
            
        if self.cliente_em_edicao:
            self.cliente_em_edicao.nome = self.txt_nome.value
            self.cliente_em_edicao.telefone = telefone_formatado
            self.cliente_em_edicao.endereco = self.txt_endereco.value
            ClienteRepository.update(self.cliente_em_edicao)
            msg, cor = 'Cliente atualizado com sucesso!', ft.Colors.ORANGE_800
        else:
            novo_cliente = Cliente(
                nome=self.txt_nome.value,
                telefone=telefone_formatado,
                endereco=self.txt_endereco.value
            )
            ClienteRepository.create(novo_cliente)
            msg, cor = 'Cliente cadastrado com sucesso!', ft.Colors.GREEN_700
        
        self.fechar_modal()
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=cor)
        self.page.snack_bar.open = True
        
        if self.on_success:
            self.on_success()
