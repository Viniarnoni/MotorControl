import flet as ft
from datetime import date
from src.models.entities import Motor
from src.repositories.motor_repo import MotorRepository

class MainView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = 'OficinaMotor — Gestão de Oficina'
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        # Campos com filtros de entrada (Máscaras de bloqueio)
        self.txt_tipo = ft.TextField(label='Equipamento/Tipo', hint_text='Ex: Bomba de Piscina, Betoneira', border_color=ft.Colors.GREY_700)
        self.txt_marca = ft.TextField(label='Marca', hint_text='Ex: WEG, Dancor, Nova', border_color=ft.Colors.GREY_700)
        self.txt_modelo = ft.TextField(label='Modelo', border_color=ft.Colors.GREY_700)
        
        self.txt_cv = ft.TextField(
            label='Potência (CV)', 
            hint_text='Ex: 1/2, 1.5, 2', 
            border_color=ft.Colors.GREY_700,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\/\.]", replacement_string="")
        )
        
        self.txt_rpm = ft.TextField(
            label='Rotação (RPM)', 
            hint_text='Ex: 3500, 1750', 
            border_color=ft.Colors.GREY_700,
            max_length=4,
            input_filter=ft.NumbersOnlyInputFilter()
        )
        
        self.txt_tensao = ft.TextField(
            label='Tensão/Voltagem', 
            hint_text='Ex: 110, 220, 110/220', 
            border_color=ft.Colors.GREY_700,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\/]", replacement_string="")
        )
        
        self.txt_serie = ft.TextField(label='Nº de série (Opcional)', border_color=ft.Colors.GREY_700)
        self.txt_problema = ft.TextField(label='Problema relatado', multiline=True, min_lines=2, border_color=ft.Colors.GREY_700)
        
        # Lista de motores cadastrados na tela
        self.lista_motores_vazia = ft.Text('Nenhum motor cadastrado ainda...', color=ft.Colors.GREY_400)
        self.coluna_listagem = ft.Column([self.lista_motores_vazia], spacing=10)
        
        # Dropdown do Cliente definido corretamente
        self.dropdown_cliente = ft.Dropdown(
            hint_text='Selecione o cliente',
            options=[ft.dropdown.Option('Cliente Padrão Balcão')],
            border_color=ft.Colors.BLUE_700,
            value='Cliente Padrão Balcão'
        )
        
        # Modal para Cadastrar Motor
        self.modal_novo_motor = ft.AlertDialog(
            title=ft.Text('Novo motor / Equipamento', weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=600,
                height=550,
                content=ft.ListView([
                    ft.Text('Cliente *', size=12, color=ft.Colors.BLUE_400),
                    self.dropdown_cliente,
                    ft.Row([self.txt_tipo, self.txt_marca], spacing=10, expand=True),
                    ft.Row([self.txt_modelo, self.txt_cv], spacing=10, expand=True),
                    ft.Row([self.txt_rpm, self.txt_tensao], spacing=10, expand=True),
                    self.txt_serie,
                    self.txt_problema,
                ], spacing=15)
            ),
            actions=[
                ft.TextButton('Cancelar', on_click=self.fechar_modal),
                ft.ElevatedButton('Salvar no Banco', bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_motor)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
    def abrir_modal(self, e):
        if self.modal_novo_motor not in self.page.overlay:
            self.page.overlay.append(self.modal_novo_motor)
        self.modal_novo_motor.open = True
        self.page.update()
        
    def fechar_modal(self, e):
        self.modal_novo_motor.open = False
        self.page.update()
        
    def salvar_motor(self, e):
        if not self.txt_tipo.value or not self.txt_marca.value:
            snack = ft.SnackBar(ft.Text('Por favor, preencha Tipo e Marca!'), bgcolor=ft.Colors.ORANGE_800)
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return

        motores_existentes = MotorRepository.get_all_active()
        for m in motores_existentes:
            # CORREÇÃO: Comparamos apenas os atributos diretos do motor para evitar o erro de Lazy Loading do SQLAlchemy
            if (
                m.tipo.lower() == self.txt_tipo.value.lower() and 
                m.marca.lower() == self.txt_marca.value.lower() and 
                (m.modelo or "").lower() == (self.txt_modelo.value or "").lower() and 
                str(m.cv or "").lower() == str(self.txt_cv.value or "").lower() and 
                str(m.rpm or "").lower() == str(self.txt_rpm.value or "").lower() and 
                str(m.tensao or "").lower() == str(self.txt_tensao.value or "").lower()
            ):
                snack_erro = ft.SnackBar(
                    ft.Text('Erro: Já existe um equipamento cadastrado com essas mesmas especificações!'),
                    bgcolor=ft.Colors.RED_800
                )
                self.page.overlay.append(snack_erro)
                snack_erro.open = True
                self.page.update()
                return
            
        novo = Motor(
            tipo=self.txt_tipo.value,
            marca=self.txt_marca.value,
            modelo=self.txt_modelo.value,
            cv=self.txt_cv.value,
            rpm=self.txt_rpm.value,
            tensao=self.txt_tensao.value,
            numero_serie=self.txt_serie.value,
            problema_relatado=self.txt_problema.value
        )
        
        MotorRepository.create(novo)
        
        self.txt_tipo.value = ''
        self.txt_marca.value = ''
        self.txt_modelo.value = ''
        self.txt_cv.value = ''
        self.txt_rpm.value = ''
        self.txt_tensao.value = ''
        self.txt_serie.value = ''
        self.txt_problema.value = ''
        
        self.fechar_modal(e)
        self.atualizar_lista_tela()
        
        snack_sucesso = ft.SnackBar(ft.Text('Motor cadastrado e salvo com sucesso!'), bgcolor=ft.Colors.GREEN_700)
        self.page.overlay.append(snack_sucesso)
        snack_sucesso.open = True
        self.page.update()
        
    def atualizar_lista_tela(self):
        lista = MotorRepository.get_all_active()
        if lista:
            self.coluna_listagem.controls.clear()
            for item in lista:
                prob = item.problema_relatado if item.problema_relatado else 'Não informado'
                card = ft.Card(
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f'{item.tipo} - {item.marca} {item.modelo}', size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(ft.Text(item.status, size=11), bgcolor=ft.Colors.BLUE_900, padding=5, border_radius=5)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f'Dados Técnicos: {item.cv} CV | {item.rpm} RPM | {item.tensao}', color=ft.Colors.GREY_400, size=13),
                            ft.Text(f'Problema: {prob}', color=ft.Colors.RED_300, size=12)
                        ], spacing=5)
                    ),
                    bgcolor=ft.Colors.GREY_900
                )
                self.coluna_listagem.controls.append(card)
            self.page.update()
            
    def build(self):
        self.atualizar_lista_tela()
        
        sidebar = ft.NavigationRail(
            selected_index=1,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            leading=ft.Icon(ft.Icons.BUILD_ROUNDED, color=ft.Colors.BLUE_400, size=32),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_ROUNDED, label='Dashboard'),
                ft.NavigationRailDestination(icon=ft.Icons.ENGINEERING_ROUNDED, label='Motores'),
                ft.NavigationRailDestination(icon=ft.Icons.PEOPLE_ROUNDED, label='Clientes'),
            ]
        )
        
        content_area = ft.Container(
            expand=True,
            padding=30,
            content=ft.Column([
                ft.Row([
                    ft.Text('Motores e Equipamentos', size=28, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        'Novo motor', 
                        icon=ft.Icons.ADD, 
                        bgcolor=ft.Colors.BLUE_700,
                        color=ft.Colors.WHITE,
                        on_click=self.abrir_modal
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=20, color=ft.Colors.GREY_800),
                self.coluna_listagem
            ], scroll=ft.ScrollMode.ALWAYS)
        )
        
        return ft.Row([sidebar, ft.VerticalDivider(width=1, color=ft.Colors.GREY_800), content_area], expand=True)
