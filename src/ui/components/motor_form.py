import flet as ft
import re
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, date
from src.models.entities import Motor
from src.repositories.motor_repo import MotorRepository
from src.repositories.cliente_repo import ClienteRepository

class MotorFormModal:
    def __init__(self, page: ft.Page, on_success):
        self.page = page
        self.on_success = on_success
        self.motor_em_edicao = None
        self.caminho_foto_atual = None
        
        self.txt_tipo = ft.TextField(label='Equipamento/Tipo', hint_text='Ex: Bomba, Betoneira', border_color=ft.Colors.GREY_700, expand=True)
        self.txt_marca = ft.TextField(label='Marca', hint_text='Ex: WEG, Dancor', border_color=ft.Colors.GREY_700, expand=True)
        self.txt_modelo = ft.TextField(label='Modelo', border_color=ft.Colors.GREY_700, expand=True)
        
        # Filtro de CV corrigido: aceita apenas números, ponto e barra sem travar a digitação
        self.txt_cv = ft.TextField(
            label='Potência (CV)', hint_text='Ex: 1/2, 1.5, 2', 
            border_color=ft.Colors.GREY_700, 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\/\.]*$", replacement_string=""), 
            expand=True
        )
        
        self.txt_rpm = ft.TextField(label='Rotação (RPM)', hint_text='Ex: 3500, 1750', border_color=ft.Colors.GREY_700, max_length=4, input_filter=ft.NumbersOnlyInputFilter(), expand=True)
        
        self.dropdown_tensao = ft.Dropdown(
            label='Tensão/Voltagem',
            border_color=ft.Colors.GREY_700, expand=True,
            options=[ft.dropdown.Option('110'), ft.dropdown.Option('220'), ft.dropdown.Option('110/220'), ft.dropdown.Option('380'), ft.dropdown.Option('440')]
        )
        
        self.txt_problema = ft.TextField(label='Problema relatado', multiline=True, min_lines=2, border_color=ft.Colors.GREY_700)
        
        hoje_br = date.today().strftime("%d/%m/%Y")
        self.txt_data_entrada = ft.TextField(label='Data de Entrada', value=hoje_br, border_color=ft.Colors.GREY_700, expand=True)
        
        self.date_picker = ft.DatePicker(on_change=self.mudar_data, first_date=datetime(2020, 1, 1), last_date=datetime(2030, 12, 31))
        self.btn_calendario = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_color=ft.Colors.BLUE_400, on_click=self.abrir_calendario)
        
        self.btn_foto = ft.ElevatedButton("Anexar Foto", icon=ft.Icons.CAMERA_ALT, bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, on_click=self.escolher_foto_nativo)
        self.texto_foto = ft.Text("Nenhuma foto selecionada", size=12, color=ft.Colors.GREY_400)
        self.img_preview = ft.Image(src="", width=120, height=120, fit="contain", visible=False, border_radius=8)
        
        self.dropdown_cliente = ft.Dropdown(label='Selecione o Cliente *', border_color=ft.Colors.BLUE_700, options=[])
        self.btn_salvar_modal = ft.ElevatedButton('Salvar no Banco', bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_motor)
        
        self.modal = ft.AlertDialog(
            title=ft.Text('Novo motor / Equipamento', weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=600, height=580, # Altura levemente reduzida já que tiramos um campo
                content=ft.ListView([
                    self.dropdown_cliente,
                    ft.Row([self.txt_tipo, self.txt_marca], spacing=10),
                    ft.Row([self.txt_modelo, self.txt_cv], spacing=10),
                    ft.Row([self.txt_rpm, self.dropdown_tensao], spacing=10),
                    ft.Row([self.txt_data_entrada, self.btn_calendario], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self.txt_problema,
                    ft.Divider(color=ft.Colors.GREY_800),
                    ft.Row([
                        ft.Column([self.btn_foto, self.texto_foto], spacing=5, expand=True),
                        self.img_preview
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], spacing=15)
            ),
            actions=[ft.TextButton('Cancelar', on_click=self.fechar_modal)],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.modal.actions.append(self.btn_salvar_modal)

    def carregar_clientes_no_dropdown(self):
        clientes = ClienteRepository.get_all_active()
        opcoes = [ft.dropdown.Option("Cliente Padrão Balcão")]
        for c in clientes:
            opcoes.append(ft.dropdown.Option(c.nome))
        self.dropdown_cliente.options = opcoes

    def abrir_calendario(self, e):
        if self.date_picker not in self.page.overlay:
            self.page.overlay.append(self.date_picker)
        self.date_picker.open = True
        self.page.update()

    def mudar_data(self, e):
        if self.date_picker.value:
            if isinstance(self.date_picker.value, str):
                dt = datetime.fromisoformat(self.date_picker.value.replace("Z", ""))
                self.txt_data_entrada.value = dt.strftime("%d/%m/%Y")
            else:
                self.txt_data_entrada.value = self.date_picker.value.strftime("%d/%m/%Y")
            self.page.update()

    def escolher_foto_nativo(self, e):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        caminho_selecionado = filedialog.askopenfilename(title="Selecione a foto", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.webp")])
        root.destroy()
        if caminho_selecionado:
            pasta_destino = os.path.join(os.getcwd(), "assets", "fotos")
            os.makedirs(pasta_destino, exist_ok=True)
            nome_arquivo = os.path.basename(caminho_selecionado)
            caminho_final = os.path.join(pasta_destino, nome_arquivo)
            shutil.copy(caminho_selecionado, caminho_final)
            self.caminho_foto_atual = os.path.abspath(caminho_final)
            self.texto_foto.value = f"Foto anexada: {nome_arquivo}"
            self.texto_foto.color = ft.Colors.GREEN_400
            self.img_preview.src = self.caminho_foto_atual
            self.img_preview.visible = True
            self.page.update()

    def fechar_modal(self, e=None):
        self.modal.open = False
        self.page.update()

    def limpar_campos(self):
        # Referência ao txt_serie removida daqui
        for txt in [self.txt_tipo, self.txt_marca, self.txt_modelo, self.txt_cv, self.txt_rpm, self.txt_problema]:
            txt.value = ''
        self.dropdown_tensao.value = None
        self.dropdown_cliente.value = "Cliente Padrão Balcão"
        self.caminho_foto_atual = None
        self.texto_foto.value = "Nenhuma foto selecionada"
        self.texto_foto.color = ft.Colors.GREY_400
        self.img_preview.visible = False
        self.img_preview.src = ""
        self.txt_data_entrada.value = date.today().strftime("%d/%m/%Y")

    def abrir_para_novo(self):
        self.motor_em_edicao = None
        self.modal.title.value = 'Novo motor / Equipamento'
        self.btn_salvar_modal.text = 'Salvar no Banco'
        self.btn_salvar_modal.bgcolor = ft.Colors.BLUE_700
        self.dropdown_cliente.disabled = False
        self.txt_tipo.disabled = False
        self.txt_marca.disabled = False
        self.limpar_campos()
        self.carregar_clientes_no_dropdown()
        
        if self.modal not in self.page.overlay:
            self.page.overlay.append(self.modal)
        self.modal.open = True
        self.page.update()

    def abrir_para_editar(self, motor):
        self.motor_em_edicao = motor
        self.modal.title.value = 'Editar Motor / Equipamento'
        self.btn_salvar_modal.text = 'Salvar Alterações'
        self.btn_salvar_modal.bgcolor = ft.Colors.ORANGE_700
        self.dropdown_cliente.disabled = True
        self.txt_tipo.disabled = True
        self.txt_marca.disabled = True
        self.carregar_clientes_no_dropdown()
        
        self.txt_tipo.value = motor.tipo
        self.txt_marca.value = motor.marca
        self.txt_modelo.value = motor.modelo
        self.txt_cv.value = str(motor.cv or '')
        self.txt_rpm.value = re.sub(r"[^0-9]", "", str(motor.rpm or ''))
        
        tensao_suja = str(motor.tensao or '')
        opcoes_tensao = [opt.key for opt in self.dropdown_tensao.options]
        self.dropdown_tensao.value = tensao_suja if tensao_suja in opcoes_tensao else None
        
        if hasattr(motor, 'cliente'):
            self.dropdown_cliente.value = motor.cliente if motor.cliente in [o.key for o in self.dropdown_cliente.options] else "Cliente Padrão Balcão"
        
        self.txt_problema.value = motor.problema_relatado
        
        if motor.data_entrada:
            if isinstance(motor.data_entrada, str):
                dt = datetime.strptime(motor.data_entrada.split(" ")[0], "%Y-%m-%d")
                self.txt_data_entrada.value = dt.strftime("%d/%m/%Y")
            else:
                self.txt_data_entrada.value = motor.data_entrada.strftime("%d/%m/%Y")
        else:
            self.txt_data_entrada.value = date.today().strftime("%d/%m/%Y")
        
        self.caminho_foto_atual = motor.caminho_foto
        if self.caminho_foto_atual and os.path.exists(self.caminho_foto_atual):
            self.texto_foto.value = f"Foto atual: {os.path.basename(self.caminho_foto_atual)}"
            self.texto_foto.color = ft.Colors.GREEN_400
            self.img_preview.src = os.path.abspath(self.caminho_foto_atual)
            self.img_preview.visible = True
        else:
            self.texto_foto.value = "Nenhuma foto selecionada"
            self.texto_foto.color = ft.Colors.GREY_400
            self.img_preview.visible = False
            
        if self.modal not in self.page.overlay:
            self.page.overlay.append(self.modal)
        self.modal.open = True
        self.page.update()

    def salvar_motor(self, e):
        if not self.txt_tipo.value or not self.txt_marca.value or not self.dropdown_cliente.value:
            self.page.snack_bar = ft.SnackBar(ft.Text('Por favor, preencha Cliente, Tipo e Marca!'), bgcolor=ft.Colors.ORANGE_800)
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        tensao_final = str(self.dropdown_tensao.value or '')
        try:
            data_objeto = datetime.strptime(self.txt_data_entrada.value, "%d/%m/%Y").date()
        except ValueError:
            self.page.snack_bar = ft.SnackBar(ft.Text('Formato de data inválido! Use DD/MM/AAAA'), bgcolor=ft.Colors.RED_700)
            self.page.snack_bar.open = True
            self.page.update()
            return

        cliente_selecionado = self.dropdown_cliente.value

        if self.motor_em_edicao:
            self.motor_em_edicao.tipo = self.txt_tipo.value
            self.motor_em_edicao.marca = self.txt_marca.value
            self.motor_em_edicao.modelo = self.txt_modelo.value
            self.motor_em_edicao.cv = self.txt_cv.value
            self.motor_em_edicao.rpm = self.txt_rpm.value
            self.motor_em_edicao.tensao = tensao_final
            self.motor_em_edicao.problema_relatado = self.txt_problema.value
            self.motor_em_edicao.data_entrada = data_objeto
            if hasattr(self.motor_em_edicao, 'cliente'):
                self.motor_em_edicao.cliente = cliente_selecionado
            if self.caminho_foto_atual:
                self.motor_em_edicao.caminho_foto = self.caminho_foto_atual
            
            MotorRepository.update(self.motor_em_edicao)
            msg_sucesso, cor_snack = 'Alterações salvas com sucesso!', ft.Colors.ORANGE_800
        else:
            # Correção principal: O cliente agora é passado DIRETAMENTE na criação, evitando que o SQLModel de erro de state
            kwargs = {
                "tipo": self.txt_tipo.value, "marca": self.txt_marca.value, "modelo": self.txt_modelo.value, 
                "cv": self.txt_cv.value, "rpm": self.txt_rpm.value, "tensao": tensao_final, 
                "problema_relatado": self.txt_problema.value,
                "caminho_foto": self.caminho_foto_atual, "data_entrada": data_objeto
            }
            # Adiciona ao dicionário apenas se o nome selecionado não for nulo
            if cliente_selecionado:
                kwargs["cliente"] = cliente_selecionado
                
            novo = Motor(**kwargs)
            MotorRepository.create(novo)
            msg_sucesso, cor_snack = 'Motor registrado com sucesso!', ft.Colors.GREEN_700
        
        self.fechar_modal()
        self.page.snack_bar = ft.SnackBar(ft.Text(msg_sucesso), bgcolor=cor_snack)
        self.page.snack_bar.open = True
        if self.on_success:
            self.on_success()
