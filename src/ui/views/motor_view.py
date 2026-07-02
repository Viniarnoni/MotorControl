import flet as ft
import re
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from src.models.entities import Motor
from src.repositories.motor_repo import MotorRepository

class MotorView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.motor_em_edicao = None
        self.caminho_foto_atual = None
        
        self.txt_tipo = ft.TextField(label='Equipamento/Tipo', hint_text='Ex: Bomba, Betoneira', border_color=ft.Colors.GREY_700, expand=True)
        self.txt_marca = ft.TextField(label='Marca', hint_text='Ex: WEG, Dancor', border_color=ft.Colors.GREY_700, expand=True)
        self.txt_modelo = ft.TextField(label='Modelo', border_color=ft.Colors.GREY_700, expand=True)
        self.txt_cv = ft.TextField(label='Potência (CV)', hint_text='Ex: 1/2, 1.5, 2', border_color=ft.Colors.GREY_700, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\/\.]", replacement_string=""), expand=True)
        self.txt_rpm = ft.TextField(label='Rotação (RPM)', hint_text='Ex: 3500, 1750', border_color=ft.Colors.GREY_700, max_length=4, input_filter=ft.NumbersOnlyInputFilter(), expand=True)
        
        self.dropdown_tensao = ft.Dropdown(
            label='Tensão/Voltagem',
            border_color=ft.Colors.GREY_700,
            expand=True,
            options=[
                ft.dropdown.Option('110'),
                ft.dropdown.Option('220'),
                ft.dropdown.Option('110/220'),
                ft.dropdown.Option('380'),
                ft.dropdown.Option('440'),
            ]
        )
        
        self.txt_serie = ft.TextField(label='Nº de série (Opcional)', border_color=ft.Colors.GREY_700)
        self.txt_problema = ft.TextField(label='Problema relatado', multiline=True, min_lines=2, border_color=ft.Colors.GREY_700)
        
        self.btn_foto = ft.ElevatedButton("Anexar Foto", icon=ft.Icons.CAMERA_ALT, bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, on_click=self.escolher_foto_nativo)
        self.texto_foto = ft.Text("Nenhuma foto selecionada", size=12, color=ft.Colors.GREY_400)
        
        self.lista_motores_vazia = ft.Text('Nenhum motor registado ainda...', color=ft.Colors.GREY_400)
        self.coluna_listagem = ft.Column([self.lista_motores_vazia], spacing=10)
        self.dropdown_cliente = ft.Dropdown(hint_text='Selecione o cliente', options=[ft.dropdown.Option('Cliente Padrão Balcão')], border_color=ft.Colors.BLUE_700, value='Cliente Padrão Balcão')
        self.btn_salvar_modal = ft.ElevatedButton('Salvar no Banco', bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_motor)
        
        self.modal_novo_motor = ft.AlertDialog(
            title=ft.Text('Novo motor / Equipamento', weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=600, height=600,
                content=ft.ListView([
                    ft.Text('Cliente *', size=12, color=ft.Colors.BLUE_400),
                    self.dropdown_cliente,
                    ft.Row([self.txt_tipo, self.txt_marca], spacing=10),
                    ft.Row([self.txt_modelo, self.txt_cv], spacing=10),
                    ft.Row([self.txt_rpm, self.dropdown_tensao], spacing=10),
                    self.txt_serie, self.txt_problema,
                    ft.Divider(color=ft.Colors.GREY_800),
                    ft.Row([self.btn_foto, self.texto_foto], alignment=ft.MainAxisAlignment.START)
                ], spacing=15)
            ),
            actions=[ft.TextButton('Cancelar', on_click=self.fechar_modal), self.btn_salvar_modal],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.motor_para_excluir = None
        self.modal_confirmar_exclusao = ft.AlertDialog(
            title=ft.Text('Confirmar Exclusão'),
            content=ft.Text('Tem a certeza de que deseja remover este equipamento?'),
            actions=[
                ft.TextButton('Cancelar', on_click=self.fechar_modal_exclusao),
                ft.ElevatedButton('Excluir', bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=self.confirmar_exclusao)
            ]
        )
        
    def escolher_foto_nativo(self, e):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        caminho_selecionado = filedialog.askopenfilename(
            title="Selecione a foto do motor",
            filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.webp")]
        )
        root.destroy()
        
        if caminho_selecionado:
            pasta_destino = os.path.join(os.getcwd(), "assets", "fotos")
            os.makedirs(pasta_destino, exist_ok=True)
            
            nome_arquivo = os.path.basename(caminho_selecionado)
            caminho_final = os.path.join(pasta_destino, nome_arquivo)
            
            shutil.copy(caminho_selecionado, caminho_final)
            
            self.caminho_foto_atual = f"assets/fotos/{nome_arquivo}"
            self.texto_foto.value = f"Foto anexada: {nome_arquivo}"
            self.texto_foto.color = ft.Colors.GREEN_400
            self.page.update()
        
    def abrir_modal(self, e):
        self.motor_em_edicao = None
        self.modal_novo_motor.title.value = 'Novo motor / Equipamento'
        self.btn_salvar_modal.text = 'Salvar no Banco'
        self.btn_salvar_modal.bgcolor = ft.Colors.BLUE_700
        
        self.dropdown_cliente.disabled = False
        self.txt_tipo.disabled = False
        self.txt_marca.disabled = False
        
        self.limpar_campos()
        if self.modal_novo_motor not in self.page.overlay:
            self.page.overlay.append(self.modal_novo_motor)
        self.modal_novo_motor.open = True
        self.page.update()
        
    def fechar_modal(self, e):
        self.modal_novo_motor.open = False
        self.page.update()
        
    def limpar_campos(self):
        for txt in [self.txt_tipo, self.txt_marca, self.txt_modelo, self.txt_cv, self.txt_rpm, self.txt_serie, self.txt_problema]:
            txt.value = ''
        self.dropdown_tensao.value = None
        self.caminho_foto_atual = None
        self.texto_foto.value = "Nenhuma foto selecionada"
        self.texto_foto.color = ft.Colors.GREY_400

    def abrir_editar_motor(self, motor_selecionado):
        self.motor_em_edicao = motor_selecionado
        self.modal_novo_motor.title.value = 'Editar Motor / Equipamento'
        self.btn_salvar_modal.text = 'Salvar Alterações'
        self.btn_salvar_modal.bgcolor = ft.Colors.ORANGE_700
        
        self.dropdown_cliente.disabled = True
        self.txt_tipo.disabled = True
        self.txt_marca.disabled = True
        
        self.txt_tipo.value = motor_selecionado.tipo
        self.txt_marca.value = motor_selecionado.marca
        self.txt_modelo.value = motor_selecionado.modelo
        
        cv_sujo = str(motor_selecionado.cv or '')
        self.txt_cv.value = re.sub(r"[^0-9\/\.]", "", cv_sujo)
        
        rpm_sujo = str(motor_selecionado.rpm or '')
        self.txt_rpm.value = re.sub(r"[^0-9]", "", rpm_sujo)
        
        tensao_suja = str(motor_selecionado.tensao or '')
        opcoes_tensao = [opt.key for opt in self.dropdown_tensao.options]
        self.dropdown_tensao.value = tensao_suja if tensao_suja in opcoes_tensao else None
        
        self.txt_serie.value = motor_selecionado.numero_serie
        self.txt_problema.value = motor_selecionado.problema_relatado
        
        self.caminho_foto_atual = motor_selecionado.caminho_foto
        if self.caminho_foto_atual:
            nome = os.path.basename(self.caminho_foto_atual)
            self.texto_foto.value = f"Foto atual: {nome}"
            self.texto_foto.color = ft.Colors.GREEN_400
        else:
            self.texto_foto.value = "Nenhuma foto selecionada"
            self.texto_foto.color = ft.Colors.GREY_400
        
        if self.modal_novo_motor not in self.page.overlay:
            self.page.overlay.append(self.modal_novo_motor)
        self.modal_novo_motor.open = True
        self.page.update()

    def abrir_excluir_motor(self, motor_selecionado):
        self.motor_para_excluir = motor_selecionado
        if self.modal_confirmar_exclusao not in self.page.overlay:
            self.page.overlay.append(self.modal_confirmar_exclusao)
        self.modal_confirmar_exclusao.open = True
        self.page.update()

    def fechar_modal_exclusao(self, e):
        self.modal_confirmar_exclusao.open = False
        self.page.update()

    def confirmar_exclusao(self, e):
        if self.motor_para_excluir:
            MotorRepository.desativar(self.motor_para_excluir.id)
            self.fechar_modal_exclusao(e)
            self.atualizar_lista_tela()
            snack = ft.SnackBar(ft.Text('Equipamento movido para o Histórico!'), bgcolor=ft.Colors.RED_700)
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()

    def salvar_motor(self, e):
        if not self.txt_tipo.value or not self.txt_marca.value:
            snack = ft.SnackBar(ft.Text('Por favor, preencha Tipo e Marca!'), bgcolor=ft.Colors.ORANGE_800)
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return
            
        tensao_final = str(self.dropdown_tensao.value or '')

        if self.motor_em_edicao:
            self.motor_em_edicao.tipo = self.txt_tipo.value
            self.motor_em_edicao.marca = self.txt_marca.value
            self.motor_em_edicao.modelo = self.txt_modelo.value
            self.motor_em_edicao.cv = self.txt_cv.value
            self.motor_em_edicao.rpm = self.txt_rpm.value
            self.motor_em_edicao.tensao = tensao_final
            self.motor_em_edicao.numero_serie = self.txt_serie.value
            self.motor_em_edicao.problema_relatado = self.txt_problema.value
            if self.caminho_foto_atual:
                self.motor_em_edicao.caminho_foto = self.caminho_foto_atual
            
            MotorRepository.update(self.motor_em_edicao)
            msg_sucesso, cor_snack = 'Alterações salvas com sucesso!', ft.Colors.ORANGE_800
        else:
            novo = Motor(
                tipo=self.txt_tipo.value, 
                marca=self.txt_marca.value, 
                modelo=self.txt_modelo.value, 
                cv=self.txt_cv.value, 
                rpm=self.txt_rpm.value, 
                tensao=tensao_final, 
                numero_serie=self.txt_serie.value, 
                problema_relatado=self.txt_problema.value,
                caminho_foto=self.caminho_foto_atual
            )
            MotorRepository.create(novo)
            msg_sucesso, cor_snack = 'Motor registado e salvo com sucesso!', ft.Colors.GREEN_700
        
        self.limpar_campos()
        self.fechar_modal(e)
        self.atualizar_lista_tela()
        snack_sucesso = ft.SnackBar(ft.Text(msg_sucesso), bgcolor=cor_snack)
        self.page.overlay.append(snack_sucesso)
        snack_sucesso.open = True
        self.page.update()
        
    def atualizar_lista_tela(self):
        lista = MotorRepository.get_all_active()
        self.coluna_listagem.controls.clear()
        if lista:
            for item in lista:
                prob = item.problema_relatado if item.problema_relatado else 'Não informado'
                
                # CORREÇÃO AQUI: Passando o ícone de forma posicional sem o 'name='
                icone_foto = ft.Icon(ft.Icons.IMAGE, color=ft.Colors.GREEN_400, size=18, tooltip="Possui foto") if item.caminho_foto else ft.Container()
                
                card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Column([
                                    ft.Row([
                                        ft.Text(f'{item.tipo} - {item.marca} {item.modelo}', size=16, weight=ft.FontWeight.BOLD),
                                        ft.Container(ft.Text(item.status, size=11), bgcolor=ft.Colors.BLUE_900, padding=5, border_radius=5),
                                        icone_foto
                                    ], spacing=10),
                                    ft.Text(f'Dados Técnicos: {item.cv} CV | {item.rpm} RPM | {item.tensao}V', color=ft.Colors.GREY_400, size=13),
                                    ft.Text(f'Problema: {prob}', color=ft.Colors.RED_300, size=12)
                                ], expand=True),
                                ft.Row([
                                    ft.IconButton(icon=ft.Icons.EDIT_ROUNDED, icon_color=ft.Colors.ORANGE_400, tooltip='Editar', on_click=lambda e, i=item: self.abrir_editar_motor(i)),
                                    ft.IconButton(icon=ft.Icons.DELETE_ROUNDED, icon_color=ft.Colors.RED_400, tooltip='Remover', on_click=lambda e, i=item: self.abrir_excluir_motor(i))
                                ], alignment=ft.MainAxisAlignment.END)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ], spacing=5)
                    ), bgcolor=ft.Colors.GREY_900
                )
                self.coluna_listagem.controls.append(card)
        else:
            self.coluna_listagem.controls.append(self.lista_motores_vazia)
        self.page.update()
            
    def build(self):
        self.atualizar_lista_tela()
        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Row([
                    ft.Text('Motores e Equipamentos', size=28, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton('Novo motor', icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.abrir_modal)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=20, color=ft.Colors.GREY_800),
                self.coluna_listagem
            ], scroll=ft.ScrollMode.ALWAYS)
        )
