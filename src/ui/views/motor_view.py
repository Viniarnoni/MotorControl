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
            hint_text="Buscar por marca, modelo ou cliente...",
            prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.BLUE_700, expand=True,
            on_change=lambda e: self.atualizar_lista_tela()
        )

        self.txt_busca_historico = ft.TextField(
            hint_text="Pesquisar por Marca, Modelo ou Cliente...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.BLUE_700,
            expand=True,
            on_change=lambda e: self.atualizar_busca_rastreabilidade()
        )
        
        self.lista_vazia = ft.Text('Nenhum motor encontrado...', color=ft.Colors.GREY_400)
        self.coluna_listagem = ft.Column([self.lista_vazia], spacing=10)
        self.lista_motores_rastreabilidade = ft.Column(spacing=10)
        self.coluna_historico_motor = ft.Column(spacing=10)
        self.motor_selecionado_historico = None
        
        self.motor_para_excluir = None
        self.modal_exclusao = ft.AlertDialog(
            title=ft.Text('Confirmar Exclusão'),
            content=ft.Text('Tem certeza de que deseja remover este motor?'),
            actions=[
                ft.TextButton('Cancelar', on_click=self.fechar_modal_exclusao),
                ft.Button('Excluir', bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE, on_click=self.confirmar_exclusao)
            ]
        )
        
        self.img_foto_ampliada = ft.Image(src="", fit="contain", height=400)
        self.modal_ver_foto = ft.AlertDialog(
            title=ft.Text('Visualizar Foto'),
            content=ft.Container(content=self.img_foto_ampliada, width=500, height=400),
            actions=[ft.TextButton('Fechar', on_click=lambda e: self.fechar_modal_foto())],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.btn_aba_cadastro = ft.Button(
            "Motores Cadastrados",
            icon=ft.Icons.LIST_ALT,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            on_click=self.mostrar_aba_cadastro,
        )
        self.btn_aba_rastreabilidade = ft.Button(
            "Rastreabilidade / Histórico",
            icon=ft.Icons.HISTORY,
            bgcolor=ft.Colors.GREY_800,
            color=ft.Colors.WHITE,
            on_click=self.mostrar_aba_rastreabilidade,
        )
        self.area_conteudo = ft.Container(expand=True)

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
            motor_id = (
                self.motor_para_excluir.id
                if hasattr(self.motor_para_excluir, "id")
                else self.motor_para_excluir
            )
            MotorRepository.desativar(motor_id)
            self.motor_para_excluir = None
            self.fechar_modal_exclusao()
            self.atualizar_lista_tela()
            self.page.snack_bar = ft.SnackBar(ft.Text('Motor arquivado!'), bgcolor=ft.Colors.RED_700)
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

    def atualizar_lista_tela(self, atualizar_pagina=True):
        lista = MotorRepository.get_all_active()
        termo = self.txt_busca.value.lower() if self.txt_busca.value else ""
        
        if termo:
            lista = [
                i for i in lista if
                termo in (i.marca or "").lower() or
                termo in (i.modelo or "").lower() or
                termo in (i.tipo or "").lower() or
                termo in (i.cliente or "").lower()
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
        if atualizar_pagina:
            self.page.update()

    def atualizar_busca_rastreabilidade(self, atualizar_pagina=True):
        termo = self.txt_busca_historico.value or ""
        motores = MotorRepository.buscar_para_rastreabilidade(termo)

        self.lista_motores_rastreabilidade.controls.clear()
        if motores:
            for motor in motores:
                self.lista_motores_rastreabilidade.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(
                                                f"{motor.marca} - {motor.modelo or motor.tipo}",
                                                weight=ft.FontWeight.BOLD,
                                                size=15,
                                            ),
                                            ft.Text(
                                                f"Cliente: {motor.cliente}",
                                                color=ft.Colors.GREY_400,
                                                size=12,
                                            ),
                                            ft.Text(
                                                f"Potência: {motor.cv or 'N/I'} CV",
                                                color=ft.Colors.GREY_500,
                                                size=12,
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                    ft.Button(
                                        "Ver Histórico",
                                        icon=ft.Icons.VISIBILITY,
                                        bgcolor=ft.Colors.BLUE_700,
                                        color=ft.Colors.WHITE,
                                        on_click=lambda e, m=motor: self.selecionar_motor_historico(m),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        )
                    )
                )
        else:
            self.lista_motores_rastreabilidade.controls.append(
                ft.Text(
                    "Nenhum motor encontrado para a rastreabilidade.",
                    color=ft.Colors.GREY_400,
                    italic=True,
                )
            )

        if atualizar_pagina:
            self.page.update()

    def _cor_status_historico(self, status: str):
        if status == "Aprovado":
            return ft.Colors.GREEN_400
        if status == "Finalizado":
            return ft.Colors.BLUE_400
        if status == "Pendente":
            return ft.Colors.AMBER_400
        return ft.Colors.RED_400

    def selecionar_motor_historico(self, motor):
        self.motor_selecionado_historico = motor
        historico = MotorRepository.obter_historico_por_motor(motor.id)

        self.coluna_historico_motor.controls.clear()
        self.coluna_historico_motor.controls.append(
            ft.Container(
                padding=15,
                bgcolor=ft.Colors.GREY_900,
                border_radius=10,
                content=ft.Column(
                    [
                        ft.Text(
                            f"Histórico do Motor: {motor.marca} - {motor.modelo or motor.tipo}",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(f"Cliente: {motor.cliente}", color=ft.Colors.GREY_400),
                        ft.Text(
                            f"Problema atual cadastrado: {motor.problema_relatado or 'Não informado'}",
                            color=ft.Colors.ORANGE_300,
                            size=12,
                        ),
                    ],
                    spacing=4,
                ),
            )
        )

        if historico:
            for item in historico:
                cor_status = self._cor_status_historico(item["status"])
                data_formatada = (
                    item["data_entrada"].strftime("%d/%m/%Y")
                    if item["data_entrada"]
                    else "N/I"
                )
                self.coluna_historico_motor.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                f"Entrada: {data_formatada}",
                                                weight=ft.FontWeight.BOLD,
                                                size=14,
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    item["status"],
                                                    color=ft.Colors.WHITE,
                                                    size=11,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                bgcolor=cor_status,
                                                padding=6,
                                                border_radius=6,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Text(
                                        f"Problema / Serviço: {item['problema_ou_servico']}",
                                        color=ft.Colors.GREY_300,
                                        size=13,
                                    ),
                                    ft.Text(
                                        f"Valor total cobrado: R$ {item['valor_total']:.2f}",
                                        color=ft.Colors.GREEN_400,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ],
                                spacing=8,
                            ),
                        )
                    )
                )
        else:
            self.coluna_historico_motor.controls.append(
                ft.Text(
                    "Nenhum orçamento anterior encontrado para este motor.",
                    color=ft.Colors.GREY_400,
                    italic=True,
                )
            )

        self.page.update()

    def _build_cadastro_content(self):
        return ft.Column([
            ft.Row([
                ft.Text('Motores', size=28, weight=ft.FontWeight.BOLD),
                ft.Button('Novo motor', icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.abrir_novo_motor)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Row([self.txt_busca], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=15, color=ft.Colors.GREY_800),
            self.coluna_listagem
        ], scroll=ft.ScrollMode.ALWAYS)

    def _build_rastreabilidade_content(self):
        return ft.Column(
            [
                ft.Text('Rastreabilidade / Histórico por Motor', size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    'Pesquise pela marca, modelo ou cliente e selecione o motor para ver todas as manutenções vinculadas.',
                    color=ft.Colors.GREY_400,
                ),
                ft.Divider(height=15, color=ft.Colors.GREY_800),
                self.txt_busca_historico,
                ft.Container(height=10),
                ft.Text('Motores encontrados', size=18, weight=ft.FontWeight.BOLD),
                self.lista_motores_rastreabilidade,
                ft.Container(height=20),
                ft.Text('Linha do Tempo / Histórico', size=18, weight=ft.FontWeight.BOLD),
                self.coluna_historico_motor,
            ],
            scroll=ft.ScrollMode.ALWAYS,
        )

    def mostrar_aba_cadastro(self, e=None, atualizar_pagina=True):
        self.btn_aba_cadastro.bgcolor = ft.Colors.BLUE_700
        self.btn_aba_rastreabilidade.bgcolor = ft.Colors.GREY_800
        self.area_conteudo.content = self._build_cadastro_content()
        self.atualizar_lista_tela(atualizar_pagina=False)
        if atualizar_pagina:
            self.page.update()

    def mostrar_aba_rastreabilidade(self, e=None, atualizar_pagina=True):
        self.btn_aba_cadastro.bgcolor = ft.Colors.GREY_800
        self.btn_aba_rastreabilidade.bgcolor = ft.Colors.BLUE_700
        self.area_conteudo.content = self._build_rastreabilidade_content()
        self.atualizar_busca_rastreabilidade(atualizar_pagina=False)
        if atualizar_pagina:
            self.page.update()
            
    def build(self):
        self.mostrar_aba_cadastro(atualizar_pagina=False)
        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Row([self.btn_aba_cadastro, self.btn_aba_rastreabilidade], spacing=10),
                ft.Divider(height=15, color=ft.Colors.GREY_800),
                self.area_conteudo
            ], scroll=ft.ScrollMode.ALWAYS)
        )
