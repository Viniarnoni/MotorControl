import flet as ft
import re
from src.models.entities import Cliente
from src.repositories.cliente_repo import ClienteRepository

class ClienteFormModal:
    def __init__(self, page: ft.Page, on_success):
        self.page = page
        self.on_success = on_success
        self.cliente_em_edicao = None
        
        self.txt_nome = ft.TextField(label='Nome Completo / Razão Social *', border_color=ft.Colors.GREY_700)

        self.txt_gov_id = ft.TextField(
            label='CNPJ / CPF (Opcional)',
            hint_text='Ex: 12.345.678/0001-90 ou 123.456.789-00',
            border_color=ft.Colors.GREY_700,
            max_length=18,
        )
        
        self.txt_telefone = ft.TextField(
            label='Telefone / WhatsApp (Apenas números)', 
            hint_text='Ex: 11999999999', 
            border_color=ft.Colors.GREY_700,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=11
        )
        
        self.txt_endereco = ft.TextField(
            label='Rua / Logradouro (Opcional)',
            hint_text='Ex: Francisco Miletta',
            border_color=ft.Colors.GREY_700,
            expand=True,
        )
        self.txt_numero = ft.TextField(
            label='Nº',
            hint_text='154',
            border_color=ft.Colors.GREY_700,
            width=90,
        )
        self.txt_bairro = ft.TextField(
            label='Bairro (Opcional)',
            hint_text='Ex: Laranjeiras 2',
            border_color=ft.Colors.GREY_700,
        )
        self.txt_cidade = ft.TextField(
            label='Cidade (Opcional)',
            hint_text='Ex: Taquaritinga',
            border_color=ft.Colors.GREY_700,
            expand=True,
        )
        self.txt_estado = ft.TextField(
            label='Estado',
            hint_text='SP',
            border_color=ft.Colors.GREY_700,
            width=90,
            max_length=2,
        )

        self.btn_salvar = ft.Button('Salvar Cliente', bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_cliente)
        
        self.modal = ft.AlertDialog(
            title=ft.Text('Cadastrar Novo Cliente', weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=480, height=480,
                content=ft.Column([
                    self.txt_nome,
                    self.txt_gov_id,
                    self.txt_telefone,
                    ft.Row([self.txt_endereco, self.txt_numero], spacing=10),
                    self.txt_bairro,
                    ft.Row([self.txt_cidade, self.txt_estado], spacing=10),
                ], spacing=12, scroll=ft.ScrollMode.AUTO)
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
        num = re.sub(r"\D", "", num_puro)
        
        if len(num) == 11:
            return f"({num[0:2]}) {num[2:7]}-{num[7:]}"
        elif len(num) == 10:
            return f"({num[0:2]}) {num[2:6]}-{num[6:]}"
        return num

    def _limpar_campos(self):
        self.txt_nome.value = ""
        self.txt_gov_id.value = ""
        self.txt_telefone.value = ""
        self.txt_endereco.value = ""
        self.txt_numero.value = ""
        self.txt_bairro.value = ""
        self.txt_cidade.value = ""
        self.txt_estado.value = ""

    def abrir_para_novo(self):
        self.cliente_em_edicao = None
        self.modal.title.value = 'Cadastrar Novo Cliente'
        self.btn_salvar.text = 'Salvar Cliente'
        self.btn_salvar.bgcolor = ft.Colors.BLUE_700
        self._limpar_campos()
        self.abrir_modal()

    def abrir_para_editar(self, cliente):
        self.cliente_em_edicao = cliente
        self.modal.title.value = 'Editar Cliente'
        self.btn_salvar.text = 'Salvar Alterações'
        self.btn_salvar.bgcolor = ft.Colors.ORANGE_700
        self.txt_nome.value = cliente.nome
        self.txt_gov_id.value = self._gov_id_exibivel(cliente.gov_id)
        self.txt_telefone.value = re.sub(r"\D", "", cliente.telefone or "")
        self.txt_endereco.value = cliente.endereco or ""
        self.txt_numero.value = cliente.numero or ""
        self.txt_bairro.value = cliente.bairro or ""
        self.txt_cidade.value = cliente.cidade or ""
        self.txt_estado.value = cliente.estado or ""
        self.abrir_modal()

    @staticmethod
    def _gov_id_exibivel(valor: str | None) -> str:
        if not valor or valor.strip() in ("", "000.000.000-00"):
            return ""
        return valor.strip()

    @staticmethod
    def _texto_opcional(valor: str | None) -> str | None:
        limpo = (valor or "").strip()
        return limpo or None

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
            
        telefone_formatado = self.formatar_telefone(self.txt_telefone.value)
        gov_id = self._texto_opcional(self.txt_gov_id.value)
        endereco = self._texto_opcional(self.txt_endereco.value)
        numero = self._texto_opcional(self.txt_numero.value)
        bairro = self._texto_opcional(self.txt_bairro.value)
        cidade = self._texto_opcional(self.txt_cidade.value)
        estado = self._texto_opcional(self.txt_estado.value)
        if estado:
            estado = estado.upper()
            
        if self.cliente_em_edicao:
            self.cliente_em_edicao.nome = self.txt_nome.value
            self.cliente_em_edicao.gov_id = gov_id
            self.cliente_em_edicao.telefone = telefone_formatado
            self.cliente_em_edicao.endereco = endereco
            self.cliente_em_edicao.numero = numero
            self.cliente_em_edicao.bairro = bairro
            self.cliente_em_edicao.cidade = cidade
            self.cliente_em_edicao.estado = estado
            ClienteRepository.update(self.cliente_em_edicao)
            msg, cor = 'Cliente atualizado com sucesso!', ft.Colors.ORANGE_800
        else:
            novo_cliente = Cliente(
                nome=self.txt_nome.value,
                gov_id=gov_id,
                telefone=telefone_formatado,
                endereco=endereco,
                numero=numero,
                bairro=bairro,
                cidade=cidade,
                estado=estado,
            )
            ClienteRepository.create(novo_cliente)
            msg, cor = 'Cliente cadastrado com sucesso!', ft.Colors.GREEN_700
        
        self.fechar_modal()
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=cor)
        self.page.snack_bar.open = True
        
        if self.on_success:
            self.on_success()
