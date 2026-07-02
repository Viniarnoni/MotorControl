import flet as ft
from src.models.entities import PrecoServico, PrecoPeca
from src.repositories.preco_servico_repo import PrecoServicoRepository
from src.repositories.preco_peca_repo import PrecoPecaRepository

class TabelaPrecoView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, padding=20)
        self.pg = page  
        
        # --- CAMPOS SERVIÇO (Filtro para aceitar números, ponto e barras) ---
        self.txt_serv_cv = ft.TextField(
            label="Potência (CV)", 
            hint_text="Ex: 1, 1.5, 1/2", 
            width=120, 
            border_color=ft.Colors.GREY_700,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\./\\]*$", replacement_string="")
        )
        self.drop_serv_fases = ft.Dropdown(
            label="Rede/Fases", width=180, border_color=ft.Colors.GREY_700, value="Monofásico/Bifásico",
            options=[ft.dropdown.Option("Monofásico/Bifásico"), ft.dropdown.Option("Trifásico")]
        )
        self.drop_serv_polos = ft.Dropdown(
            label="Polos", width=130, border_color=ft.Colors.GREY_700, value="2 Polos",
            options=[ft.dropdown.Option("2 Polos"), ft.dropdown.Option("4 Polos"), ft.dropdown.Option("6 Polos"), ft.dropdown.Option("8 Polos")]
        )
        self.txt_serv_preco = ft.TextField(label="Preço Rebobinagem (R$)", width=160, border_color=ft.Colors.BLUE_600, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\.]*$", replacement_string=""))
        self.table_servicos = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("CV")), ft.DataColumn(ft.Text("Rede")), ft.DataColumn(ft.Text("Polos")), ft.DataColumn(ft.Text("Preço Mão de Obra")), ft.DataColumn(ft.Text("Ações"))],
            rows=[]
        )
        
        # --- CAMPOS PEÇA ---
        self.txt_peca_nome = ft.TextField(label="Nome da Peça / Componente", hint_text="Ex: Rolamento 6203", expand=True, border_color=ft.Colors.GREY_700)
        self.txt_peca_preco = ft.TextField(label="Preço Unitário (R$)", width=160, border_color=ft.Colors.BLUE_600, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\.]*$", replacement_string=""))
        self.table_pecas = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Descrição da Peça")), ft.DataColumn(ft.Text("Preço Unitário")), ft.DataColumn(ft.Text("Ações"))],
            rows=[]
        )
        
        # --- MONTAGEM DOS CONTEÚDOS ---
        self.aba_servicos = ft.Column([
            ft.Text("Cadastrar Preço de Mão de Obra / Rebobinagem", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Row([
                self.txt_serv_cv, self.drop_serv_fases, self.drop_serv_polos, self.txt_serv_preco,
                ft.ElevatedButton("Adicionar", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_servico)
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.ListView([self.table_servicos], expand=True, spacing=10)
        ], spacing=15, expand=True)

        self.aba_pecas = ft.Column([
            ft.Text("Cadastrar Peças e Componentes de Troca", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Row([
                self.txt_peca_nome, self.txt_peca_preco,
                ft.ElevatedButton("Adicionar", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_peca)
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.ListView([self.table_pecas], expand=True, spacing=10)
        ], spacing=15, expand=True)

        self.conteudo_da_aba = ft.Container(content=self.aba_servicos, expand=True)

        self.btn_servicos = ft.ElevatedButton("Mão de Obra", icon=ft.Icons.BUILD, bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE, on_click=self.clique_aba_servicos)
        self.btn_pecas = ft.TextButton("Peças e Componentes", icon=ft.Icons.SETTINGS_SUGGEST, on_click=self.clique_aba_pecas)

        self.content = ft.Column([
            ft.Row([self.btn_servicos, self.btn_pecas], spacing=10),
            ft.Divider(height=2, color=ft.Colors.GREY_800),
            self.conteudo_da_aba
        ], expand=True)
        
        self.atualizar_listas()

    def clique_aba_servicos(self, e):
        self.btn_servicos.bgcolor = ft.Colors.BLUE_800
        self.btn_servicos.color = ft.Colors.WHITE
        self.btn_pecas.bgcolor = None
        self.btn_pecas.color = None
        self.conteudo_da_aba.content = self.aba_servicos
        self.pg.update()

    def clique_aba_pecas(self, e):
        self.btn_pecas.bgcolor = ft.Colors.BLUE_800
        self.btn_pecas.color = ft.Colors.WHITE
        self.btn_servicos.bgcolor = None
        self.btn_servicos.color = None
        self.conteudo_da_aba.content = self.aba_pecas
        self.pg.update()

    def atualizar_listas(self):
        self.table_servicos.rows.clear()
        for s in PrecoServicoRepository.get_all():
            self.table_servicos.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(s.cv)),
                ft.DataCell(ft.Text(s.fases)),
                ft.DataCell(ft.Text(s.polos)),
                ft.DataCell(ft.Text(f"R$ {s.preco_rebobinagem:.2f}")),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=lambda e, sid=s.id: self.deletar_servico(sid)))
            ]))

        self.table_pecas.rows.clear()
        for p in PrecoPecaRepository.get_all():
            self.table_pecas.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p.nome)),
                ft.DataCell(ft.Text(f"R$ {p.preco_unitario:.2f}")),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=lambda e, pid=p.id: self.deletar_peca(pid)))
            ]))
        self.pg.update()

    def salvar_servico(self, e):
        if not self.txt_serv_cv.value or not self.txt_serv_preco.value:
            return
        try:
            val = float(self.txt_serv_preco.value)
            novo = PrecoServico(cv=self.txt_serv_cv.value, fases=self.drop_serv_fases.value, polos=self.drop_serv_polos.value, preco_rebobinagem=val)
            PrecoServicoRepository.create(novo)
            self.txt_serv_cv.value = ""
            self.txt_serv_preco.value = ""
            self.atualizar_listas()
        except ValueError:
            pass

    def deletar_servico(self, sid):
        PrecoServicoRepository.delete(sid)
        self.atualizar_listas()

    def salvar_peca(self, e):
        if not self.txt_peca_nome.value or not self.txt_peca_preco.value:
            return
        try:
            val = float(self.txt_peca_preco.value)
            nova = PrecoPeca(nome=self.txt_peca_nome.value, preco_unitario=val)
            PrecoPecaRepository.create(nova)
            self.txt_peca_nome.value = ""
            self.txt_peca_preco.value = ""
            self.atualizar_listas()
        except ValueError:
            pass

    def deletar_peca(self, pid):
        PrecoPecaRepository.delete(pid)
        self.atualizar_listas()
