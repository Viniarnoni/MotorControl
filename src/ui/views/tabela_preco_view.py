import flet as ft
from src.models.entities import PrecoServico, PrecoPeca
from src.repositories.preco_servico_repo import PrecoServicoRepository
from src.repositories.preco_peca_repo import PrecoPecaRepository

class TabelaPrecoView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, padding=20)
        self.pg = page  
        
        # --- VARIÁVEIS PARA A JANELA DE CONFIRMAÇÃO ---
        self.item_para_excluir_id = None
        self.item_para_excluir_tipo = None
        
        self.dlg_confirmacao = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER_400), ft.Text("Confirmar Exclusão")]),
            content=ft.Text("Tem a certeza de que deseja excluir este item permanentemente?"),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_dialogo_exclusao),
                ft.TextButton("Excluir", icon=ft.Icons.DELETE_FOREVER, icon_color=ft.Colors.RED_400, on_click=self.executar_exclusao),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # --- CAMPOS SERVIÇO ---
        self.txt_serv_cv = ft.TextField(
            label="Potência (CV)", hint_text="Ex: 1, 1.5, 1,5, 1/2", width=120, border_color=ft.Colors.GREY_700,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9\./\\,]*$", replacement_string="")
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
                ft.Button("Adicionar", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_servico)
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.ListView([self.table_servicos], expand=True, spacing=10)
        ], spacing=15, expand=True)

        self.aba_pecas = ft.Column([
            ft.Text("Cadastrar Peças e Componentes de Troca", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Row([
                self.txt_peca_nome, self.txt_peca_preco,
                ft.Button("Adicionar", icon=ft.Icons.ADD, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.salvar_peca)
            ], spacing=10, alignment=ft.MainAxisAlignment.START),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.ListView([self.table_pecas], expand=True, spacing=10)
        ], spacing=15, expand=True)

        self.conteudo_da_aba = ft.Container(content=self.aba_servicos, expand=True)

        self.btn_servicos = ft.Button("Mão de Obra", icon=ft.Icons.BUILD, bgcolor=ft.Colors.BLUE_800, color=ft.Colors.WHITE, on_click=self.clique_aba_servicos)
        self.btn_pecas = ft.TextButton("Peças e Componentes", icon=ft.Icons.SETTINGS_SUGGEST, on_click=self.clique_aba_pecas)

        self.content = ft.Column([
            ft.Row([self.btn_servicos, self.btn_pecas], spacing=10),
            ft.Divider(height=2, color=ft.Colors.GREY_800),
            self.conteudo_da_aba
        ], expand=True)
        
        self.atualizar_listas()

    # --- NOTIFICAÇÃO FLUTUANTE CUSTOMIZADA (BLINDADA VIA OVERLAY) ---
    def mostrar_snackbar(self, mensagem: str, cor: str):
        import threading
        import time

        # Define um ícone bonito baseado no tipo de mensagem
        icone = ft.Icons.INFO_ROUNDED
        if "✅" in mensagem:
            icone = ft.Icons.CHECK_CIRCLE_ROUNDED
            mensagem = mensagem.replace("✅", "").strip()
        elif "⚠️" in mensagem:
            icone = ft.Icons.WARNING_ROUNDED
            mensagem = mensagem.replace("⚠️", "").strip()

        # Cria um container flutuante customizado
        toast = ft.Container(
            content=ft.Row([
                ft.Icon(icone, color=ft.Colors.WHITE, size=20),
                ft.Text(mensagem, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=14),
            ], alignment=ft.MainAxisAlignment.START, tight=True, spacing=10),
            bgcolor=cor,
            padding=15,
            border_radius=10,
            bottom=30,  
            right=30,   
            shadow=ft.BoxShadow(blur_radius=10, color="#40000000"), 
        )

        # Adiciona à camada flutuante da página e atualiza
        self.pg.overlay.append(toast)
        self.pg.update()

        # Função em segundo plano para fazer o aviso sumir sozinho após 3 segundos
        def fechar_toast():
            time.sleep(3)
            if toast in self.pg.overlay:
                self.pg.overlay.remove(toast)
                self.pg.update()

        threading.Thread(target=fechar_toast, daemon=True).start()

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
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=lambda e, sid=s.id: self.abrir_dialogo_exclusao(sid, "servico")))
            ]))

        self.table_pecas.rows.clear()
        for p in PrecoPecaRepository.get_all():
            self.table_pecas.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p.nome)),
                ft.DataCell(ft.Text(f"R$ {p.preco_unitario:.2f}")),
                ft.DataCell(ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=lambda e, pid=p.id: self.abrir_dialogo_exclusao(pid, "peca")))
            ]))
        self.pg.update()

    def abrir_dialogo_exclusao(self, item_id, tipo):
        self.item_para_excluir_id = item_id
        self.item_para_excluir_tipo = tipo
        if self.dlg_confirmacao in self.pg.overlay:
            self.pg.overlay.remove(self.dlg_confirmacao)
        self.pg.overlay.append(self.dlg_confirmacao)
        self.dlg_confirmacao.open = True
        self.pg.update()

    def fechar_dialogo_exclusao(self, e):
        self.dlg_confirmacao.open = False
        self.item_para_excluir_id = None
        self.item_para_excluir_tipo = None
        self.pg.update()

    def executar_exclusao(self, e):
        if self.item_para_excluir_tipo == "servico":
            PrecoServicoRepository.delete(self.item_para_excluir_id)
        elif self.item_para_excluir_tipo == "peca":
            PrecoPecaRepository.delete(self.item_para_excluir_id)
            
        self.dlg_confirmacao.open = False
        self.item_para_excluir_id = None
        self.item_para_excluir_tipo = None
        self.atualizar_listas()
        
        # Mostra o aviso de exclusão
        self.mostrar_snackbar("✅ Item excluído com sucesso!", ft.Colors.AMBER_800)

    def salvar_servico(self, e):
        # Validação: Se os campos estiverem vazios, mostra erro
        if not self.txt_serv_cv.value or not self.txt_serv_preco.value:
            self.mostrar_snackbar("⚠️ Preencha a Potência e o Preço para adicionar!", ft.Colors.RED_600)
            return
        
        try:
            val = float(self.txt_serv_preco.value)
            cv_normalizado = (self.txt_serv_cv.value or "").strip().replace(",", ".")
            novo = PrecoServico(cv=cv_normalizado, fases=self.drop_serv_fases.value, polos=self.drop_serv_polos.value, preco_rebobinagem=val)
            PrecoServicoRepository.create(novo)
            
            self.txt_serv_cv.value = ""
            self.txt_serv_preco.value = ""
            self.atualizar_listas()
            
            # Mostra o aviso de sucesso
            self.mostrar_snackbar("✅ Preço de Mão de Obra cadastrado!", ft.Colors.GREEN_700)
            
        except ValueError:
            self.mostrar_snackbar("⚠️ Valor de preço inválido!", ft.Colors.RED_600)

    def salvar_peca(self, e):
        # Validação: Se os campos estiverem vazios, mostra erro
        if not self.txt_peca_nome.value or not self.txt_peca_preco.value:
            self.mostrar_snackbar("⚠️ Preencha o Nome e o Preço da peça!", ft.Colors.RED_600)
            return
            
        try:
            val = float(self.txt_peca_preco.value)
            nova = PrecoPeca(nome=self.txt_peca_nome.value, preco_unitario=val)
            PrecoPecaRepository.create(nova)
            
            self.txt_peca_nome.value = ""
            self.txt_peca_preco.value = ""
            self.atualizar_listas()
            
            # Mostra o aviso de sucesso
            self.mostrar_snackbar("✅ Peça cadastrada com sucesso!", ft.Colors.GREEN_700)
            
        except ValueError:
            self.mostrar_snackbar("⚠️ Valor de preço inválido!", ft.Colors.RED_600)
