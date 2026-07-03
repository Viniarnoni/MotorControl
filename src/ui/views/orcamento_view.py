import flet as ft
from datetime import date
from src.core.database import get_session
from src.models.entities import Motor, PrecoServico, PrecoPeca, Orcamento, ItemOrcamento
from src.repositories.preco_servico_repo import PrecoServicoRepository
from src.repositories.preco_peca_repo import PrecoPecaRepository

class OrcamentoView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, padding=20)
        self.pg = page
        
        self.editando_orcamento_id = None
        self.motores_disponiveis = []
        self.pecas_disponiveis = []
        self.itens_temporarios_pecas = []

        # --- COMPONENTES DA ABA 1: FORMULÁRIO ---
        self.drop_motores = ft.Dropdown(label="Selecione o Motor / Equipamento", expand=True, border_color=ft.Colors.BLUE_600)
        self.drop_motores.on_change = self.ao_selecionar_motor
        
        self.txt_detalhes_motor = ft.Text("Selecione um motor para exibir os detalhes.", color=ft.Colors.GREY_400, italic=True)
        
        self.switch_rebobinar = ft.Switch(label="Buscar Preço Tabela", value=False, active_color=ft.Colors.BLUE_400)
        self.switch_rebobinar.on_change = self.recalcular_mao_de_obra
        
        self.txt_valor_mo = ft.TextField(
            label="Valor Mão de Obra (R$)", value="0.00", width=200, border_color=ft.Colors.BLUE_400,
            text_align=ft.TextAlign.RIGHT, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$", replacement_string="")
        )
        self.txt_valor_mo.on_change = self.ao_mudar_valor_manual

        self.drop_pecas = ft.Dropdown(label="Peça/Componente", expand=True, border_color=ft.Colors.GREY_700)
        
        self.txt_qtd_peca = ft.TextField(
            value="1", width=50, text_align=ft.TextAlign.CENTER, 
            border_color=ft.Colors.GREY_700, content_padding=0,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
        )
        self.btn_menos = ft.IconButton(ft.Icons.REMOVE, on_click=self.subtrair_qtd, icon_size=18)
        self.btn_mais = ft.IconButton(ft.Icons.ADD, on_click=self.somar_qtd, icon_size=18)
        
        self.row_quantidade = ft.Row([
            ft.Text("Qtd:", size=14), self.btn_menos, self.txt_qtd_peca, self.btn_mais
        ], spacing=0, alignment=ft.MainAxisAlignment.START)

        self.btn_add_peca = ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.GREEN_400, icon_size=36, on_click=self.adicionar_peca_lista)
        
        self.table_itens_pecas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Descrição")), ft.DataColumn(ft.Text("Qtd")),
                ft.DataColumn(ft.Text("Unidade")), ft.DataColumn(ft.Text("Total")), ft.DataColumn(ft.Text("Ações"))
            ], rows=[]
        )

        self.txt_total_pecas = ft.Text("Total Peças: R$ 0.00", size=14, color=ft.Colors.GREY_400)
        self.txt_total_geral = ft.Text("VALOR TOTAL: R$ 0.00", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)
        self.txt_obs = ft.TextField(label="Observações / Condições de Pagamento", multiline=True, min_lines=2, max_lines=3, border_color=ft.Colors.GREY_700)

        self.btn_cancelar_edicao = ft.TextButton(
            "Cancelar Edição", icon=ft.Icons.CANCEL, icon_color=ft.Colors.RED_400, 
            visible=False, on_click=self.cancelar_edicao_ativa
        )

        self.btn_salvar = ft.Button(
            "Salvar e Emitir Orçamento", icon=ft.Icons.SAVE, bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE, height=45, on_click=self.salvar_orcamento_completo
        )

        # --- COMPONENTES DA ABA 2: HISTÓRICO ---
        self.txt_busca = ft.TextField(
            label="Buscar por cliente ou descrição do motor...", expand=True, border_color=ft.Colors.GREY_700,
            on_change=self.filtrar_orcamentos, prefix_icon=ft.Icons.SEARCH
        )
        self.lista_orcamentos_ui = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # --- ABAS ---
        self.btn_aba_novo = ft.Button("Novo Orçamento", icon=ft.Icons.ADD_TASK, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.mostrar_aba_novo)
        self.btn_aba_historico = ft.Button("Orçamentos Emitidos", icon=ft.Icons.HISTORY, bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, on_click=self.mostrar_aba_historico)
        
        self.botoes_abas = ft.Row([self.btn_aba_novo, self.btn_aba_historico], spacing=10)
        self.area_conteudo = ft.Container(content=self.criar_layout_formulario(), expand=True)

        self.content = ft.Column([
            self.botoes_abas,
            ft.Divider(color=ft.Colors.GREY_800, height=2),
            self.area_conteudo
        ], expand=True)
        
        self.carregar_dados_iniciais()

    def somar_qtd(self, e):
        try:
            atual = int(self.txt_qtd_peca.value) if self.txt_qtd_peca.value else 0
            self.txt_qtd_peca.value = str(atual + 1)
        except ValueError:
            self.txt_qtd_peca.value = "1"
        self.pg.update()

    def subtrair_qtd(self, e):
        try:
            atual = int(self.txt_qtd_peca.value) if self.txt_qtd_peca.value else 2
            if atual > 1:
                self.txt_qtd_peca.value = str(atual - 1)
        except ValueError:
            self.txt_qtd_peca.value = "1"
        self.pg.update()

    def mostrar_aba_novo(self, e):
        self.btn_aba_novo.bgcolor = ft.Colors.BLUE_700
        self.btn_aba_historico.bgcolor = ft.Colors.GREY_800
        self.area_conteudo.content = self.criar_layout_formulario()
        self.pg.update()

    def mostrar_aba_historico(self, e):
        self.btn_aba_novo.bgcolor = ft.Colors.GREY_800
        self.btn_aba_historico.bgcolor = ft.Colors.BLUE_700
        self.area_conteudo.content = self.criar_layout_historico()
        self.carregar_historico_db()

    def criar_layout_formulario(self):
        return ft.Column([
            ft.Text("Montador de Orçamentos Automático", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Row([self.drop_motores], spacing=10),
            ft.Container(
                content=ft.Column([
                    self.txt_detalhes_motor,
                    ft.Row([self.switch_rebobinar, self.txt_valor_mo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment="center")
                ]), padding=10, bgcolor=ft.Colors.GREY_900, border_radius=5
            ),
            ft.Divider(height=10, color=ft.Colors.GREY_800),
            ft.Text("Incluir Peças e Componentes na Troca", size=15, weight=ft.FontWeight.BOLD),
            ft.Row([self.drop_pecas, self.row_quantidade, self.btn_add_peca], alignment=ft.MainAxisAlignment.START, vertical_alignment="center"),
            ft.Container(content=ft.ListView([self.table_itens_pecas], expand=True), height=180),
            ft.Divider(height=10, color=ft.Colors.GREY_800),
            self.txt_obs,
            ft.Row([
                ft.Column([self.txt_total_pecas, self.txt_total_geral]),
                ft.Row([self.btn_cancelar_edicao, self.btn_salvar], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment="center")
        ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)

    def criar_layout_historico(self):
        return ft.Column([
            ft.Text("Histórico de Orçamentos do Sistema", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Row([self.txt_busca]),
            ft.Container(content=self.lista_orcamentos_ui, expand=True)
        ], spacing=15, expand=True)

    def carregar_dados_iniciais(self):
        with get_session() as session:
            from sqlmodel import select
            self.motores_disponiveis = session.exec(select(Motor).where(Motor.is_active == True)).all()
        self.pecas_disponiveis = PrecoPecaRepository.get_all()

        self.drop_motores.options.clear()
        for m in self.motores_disponiveis:
            self.drop_motores.options.append(ft.dropdown.Option(key=str(m.id), text=f"{m.cliente} -> {m.marca} ({m.cv} CV, {m.polos})"))
        
        self.drop_pecas.options.clear()
        for p in self.pecas_disponiveis:
            self.drop_pecas.options.append(ft.dropdown.Option(key=str(p.id), text=f"{p.nome} (R$ {p.preco_unitario:.2f})"))

    def carregar_historico_db(self):
        self.lista_orcamentos_ui.controls.clear()
        termo = self.txt_busca.value.lower() if self.txt_busca.value else ""
        try:
            with get_session() as session:
                from sqlmodel import select
                session.expire_all()
                orcamentos = session.exec(select(Orcamento).order_by(Orcamento.id.desc())).all()
                
                if not orcamentos:
                    self.lista_orcamentos_ui.controls.append(ft.Text("Nenhum orçamento emitido.", color=ft.Colors.GREY_500, italic=True))
                
                for o in orcamentos:
                    if termo and (termo not in o.cliente_nome.lower() and termo not in o.motor_descricao.lower()): continue
                    
                    cor_status = ft.Colors.ORANGE_700 if o.status == "Pendente" else (ft.Colors.GREEN_700 if o.status == "Aprovado" else ft.Colors.RED_700)
                    
                    card = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Row([
                                    ft.Icon(ft.Icons.RECEIPT_LONG, color=ft.Colors.BLUE_400, size=28),
                                    ft.Column([
                                        ft.Text(f"Cliente: {o.cliente_nome}", weight=ft.FontWeight.BOLD, size=15),
                                        ft.Text(f"Equipamento: {o.motor_descricao}", color=ft.Colors.GREY_400, size=13),
                                    ], spacing=2)
                                ], spacing=10),
                                ft.Row([
                                    ft.PopupMenuButton(
                                        content=ft.Container(
                                            content=ft.Text(o.status.upper(), color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD),
                                            bgcolor=cor_status, padding=5, border_radius=4
                                        ),
                                        items=[
                                            ft.PopupMenuItem(content=ft.Text("Aprovado"), icon=ft.Icons.CHECK, on_click=lambda e, oid=o.id: self.mudar_status_orcamento(oid, "Aprovado")),
                                            ft.PopupMenuItem(content=ft.Text("Pendente"), icon=ft.Icons.HOURGLASS_EMPTY, on_click=lambda e, oid=o.id: self.mudar_status_orcamento(oid, "Pendente")),
                                            ft.PopupMenuItem(content=ft.Text("Reprovado"), icon=ft.Icons.CLOSE, on_click=lambda e, oid=o.id: self.mudar_status_orcamento(oid, "Reprovado")),
                                        ]
                                    ),
                                    # BOTÃO DO WHATSAPP REINTEGRADO
                                    ft.IconButton(
                                        icon=ft.Icons.CHAT, icon_color=ft.Colors.GREEN_500,
                                        tooltip="Enviar via WhatsApp", on_click=lambda e, oid=o.id, nome=o.cliente_nome: self.emitir_e_enviar_whatsapp(oid, nome)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.PRINT, icon_color=ft.Colors.GREEN_400,
                                        tooltip="Gerar PDF / Imprimir", on_click=lambda e, oid=o.id: self.emitir_pdf_orcamento(oid)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CREATE, icon_color=ft.Colors.BLUE_400,
                                        tooltip="Editar Orçamento", on_click=lambda e, oid=o.id: self.carregar_orcamento_para_edicao(oid)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400,
                                        tooltip="Excluir Orçamento", on_click=lambda e, oid=o.id: self.excluir_orcamento(oid)
                                    )
                                ], spacing=5)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(color=ft.Colors.GREY_800, height=10),
                            ft.Row([
                                ft.Text(f"Mão de Obra: R$ {o.valor_mao_de_obra:.2f}", color=ft.Colors.GREY_400, size=12),
                                ft.Text(f"Peças: R$ {o.valor_pecas:.2f}", color=ft.Colors.GREY_400, size=12),
                                ft.Text(f"TOTAL: R$ {o.valor_total:.2f}", color=ft.Colors.GREEN_400, weight=ft.FontWeight.BOLD, size=14),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ]),
                        bgcolor=ft.Colors.GREY_900, padding=15, border_radius=6
                    )
                    self.lista_orcamentos_ui.controls.append(card)
        except Exception as ex:
            self.lista_orcamentos_ui.controls.append(ft.Text(f"Erro: {str(ex)}", color=ft.Colors.RED_400))
        self.pg.update()

    def mudar_status_orcamento(self, orcamento_id, novo_status):
        try:
            with get_session() as session:
                orcamento = session.get(Orcamento, orcamento_id)
                if orcamento:
                    orcamento.status = novo_status
                    session.add(orcamento)
                    session.commit()
            self.carregar_historico_db()
        except Exception as ex:
            print(f"Erro ao mudar status: {ex}")

    def emitir_e_enviar_whatsapp(self, orcamento_id, cliente_nome):
        """Chama a geração de PDF e o envio pelo WhatsApp resolvendo o telefone dinamicamente."""
        try:
            from src.services.pdf_service import PDFService
            caminho = PDFService.gerar_pdf(orcamento_id)
            PDFService.enviar_whatsapp(caminho, cliente_nome)
        except Exception as ex:
            self.txt_busca.value = f"Erro ao enviar WhatsApp: {str(ex)}"
            self.txt_busca.update()

    def emitir_pdf_orcamento(self, orcamento_id):
        try:
            from src.services.pdf_service import PDFService
            caminho = PDFService.gerar_pdf(orcamento_id)
            PDFService.abrir_pdf(caminho)
        except Exception as ex:
            self.txt_busca.value = f"Erro ao gerar PDF: {str(ex)}"
            self.txt_busca.update()

    def carregar_orcamento_para_edicao(self, orcamento_id):
        try:
            with get_session() as session:
                from sqlmodel import select
                orcamento = session.get(Orcamento, orcamento_id)
                if not orcamento: return
                
                self.editando_orcamento_id = orcamento_id
                self.drop_motores.value = str(orcamento.motor_id)
                self.txt_valor_mo.value = f"{orcamento.valor_mao_de_obra:.2f}"
                self.switch_rebobinar.value = False
                self.txt_obs.value = orcamento.observacoes or ""
                
                itens = session.exec(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)).all()
                self.itens_temporarios_pecas.clear()
                for item in itens:
                    self.itens_temporarios_pecas.append({
                        "nome": item.descricao, "qtd": item.quantidade,
                        "preco_uni": item.preco_unitario, "total": item.preco_total
                    })
                
                motor = next((m for m in self.motores_disponiveis if m.id == orcamento.motor_id), None)
                if motor:
                    self.txt_detalhes_motor.value = f"Especificações: {motor.tipo} {motor.marca} | {motor.cv} CV | {motor.fases} | {motor.polos}"
                    self.txt_detalhes_motor.color = ft.Colors.WHITE
                
                self.btn_salvar.text = "Atualizar Orçamento"
                self.btn_salvar.bgcolor = ft.Colors.BLUE_700
                self.btn_cancelar_edicao.visible = True
                
                self.mostrar_aba_novo(None)
                self.atualizar_totais_tela()
        except Exception as ex:
            print(ex)

    def cancelar_edicao_ativa(self, e):
        self.editando_orcamento_id = None
        self.itens_temporarios_pecas.clear()
        self.txt_valor_mo.value = "0.00"
        self.txt_obs.value = ""
        self.drop_motores.value = None
        self.txt_detalhes_motor.value = "Selecione um motor para exibir os detalhes."
        self.txt_detalhes_motor.color = ft.Colors.GREY_400
        self.btn_salvar.text = "Salvar e Emitir Orçamento"
        self.btn_salvar.bgcolor = ft.Colors.GREEN_700
        self.btn_cancelar_edicao.visible = False
        self.atualizar_totais_tela()

    def excluir_orcamento(self, orcamento_id):
        try:
            with get_session() as session:
                from sqlmodel import select
                itens = session.exec(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)).all()
                for item in itens: session.delete(item)
                orcamento = session.get(Orcamento, orcamento_id)
                if orcamento: session.delete(orcamento)
                session.commit()
            self.carregar_historico_db()
        except Exception as ex:
            print(ex)

    def filtrar_orcamentos(self, e):
        self.carregar_historico_db()

    def ao_selecionar_motor(self, e):
        if not self.drop_motores.value: return
        motor_id = int(self.drop_motores.value)
        motor = next((m for m in self.motores_disponiveis if m.id == motor_id), None)
        if motor:
            self.txt_detalhes_motor.value = f"Especificações: {motor.tipo} {motor.marca} | {motor.cv} CV | {motor.fases} | {motor.polos}"
            self.txt_detalhes_motor.color = ft.Colors.WHITE
            self.recalcular_mao_de_obra(None)

    def recalcular_mao_de_obra(self, e):
        if not self.drop_motores.value: return
        if self.switch_rebobinar.value:
            motor_id = int(self.drop_motores.value)
            motor = next((m for m in self.motores_disponiveis if m.id == motor_id), None)
            if motor:
                preco_servico = self.buscar_preco_rebobinagem(motor.cv, motor.fases, motor.polos)
                if preco_servico:
                    self.txt_valor_mo.value = f"{preco_servico.preco_rebobinagem:.2f}"
                else:
                    self.txt_valor_mo.value = "0.00"
                    self.txt_detalhes_motor.value += "\n(Aviso: Preço não encontrado)."
                    self.txt_detalhes_motor.color = ft.Colors.ORANGE_400
        else:
            if not self.editando_orcamento_id:
                self.txt_valor_mo.value = "0.00"
        
        self.txt_valor_mo.update()
        self.atualizar_totais_tela()

    def buscar_preco_rebobinagem(self, cv, fases, polos):
        for s in PrecoServicoRepository.get_all():
            if s.cv == cv and s.fases == fases and s.polos == polos: return s
        return None

    def ao_mudar_valor_manual(self, e):
        self.atualizar_totais_tela()

    def obter_valor_mo_seguro(self):
        try: return float(self.txt_valor_mo.value)
        except ValueError: return 0.0

    def adicionar_peca_lista(self, e):
        if not self.drop_pecas.value: return
        
        qtd_str = self.txt_qtd_peca.value.strip() if self.txt_qtd_peca.value else ""
        qtd = int(qtd_str) if qtd_str.isdigit() else 1
        if qtd <= 0: return
        
        peca_id = int(self.drop_pecas.value)
        peca = next((p for p in self.pecas_disponiveis if p.id == peca_id), None)
        if peca:
            self.itens_temporarios_pecas.append({"nome": peca.nome, "qtd": qtd, "preco_uni": peca.preco_unitario, "total": peca.preco_unitario * qtd})
            self.txt_qtd_peca.value = "1"
            self.drop_pecas.value = None
            self.txt_qtd_peca.update()
            self.drop_pecas.update()
            self.atualizar_totais_tela()

    def remover_peca_lista(self, idx):
        self.itens_temporarios_pecas.pop(idx)
        self.atualizar_totais_tela()

    def atualizar_totais_tela(self):
        self.table_itens_pecas.rows.clear()
        total_pecas = 0.0
        for i, item in enumerate(self.itens_temporarios_pecas):
            total_pecas += item["total"]
            self.table_itens_pecas.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["nome"])), ft.DataCell(ft.Text(str(item["qtd"]))),
                ft.DataCell(ft.Text(f"R$ {item['preco_uni']:.2f}")), ft.DataCell(ft.Text(f"R$ {item['total']:.2f}")),
                ft.DataCell(ft.IconButton(ft.Icons.DELETE_FOREVER, icon_color=ft.Colors.RED_400, on_click=lambda e, idx=i: self.remover_peca_lista(idx)))
            ]))
        total_geral = self.obter_valor_mo_seguro() + total_pecas
        self.txt_total_pecas.value = f"Total Peças: R$ {total_pecas:.2f}"
        self.txt_total_geral.value = f"VALOR TOTAL: R$ {total_geral:.2f}"
        self.pg.update()

    def salvar_orcamento_completo(self, e):
        if not self.drop_motores.value:
            self.txt_detalhes_motor.value = "⚠️ ERRO: Selecione um motor primeiro!"
            self.txt_detalhes_motor.color = ft.Colors.RED_400
            self.pg.update()
            return
            
        motor_id = int(self.drop_motores.value)
        motor = next((m for m in self.motores_disponiveis if m.id == motor_id), None)
        if not motor: return
        
        valor_mo_final = self.obter_valor_mo_seguro()
        total_pecas = sum(item["total"] for item in self.itens_temporarios_pecas)
        total_geral = valor_mo_final + total_pecas
        
        try:
            with get_session() as session:
                from sqlmodel import select
                if self.editando_orcamento_id:
                    orcamento_db = session.get(Orcamento, self.editando_orcamento_id)
                    if orcamento_db:
                        orcamento_db.motor_id = motor.id
                        orcamento_db.motor_descricao = f"{motor.marca} {motor.tipo} ({motor.cv}CV)"
                        orcamento_db.cliente_nome = motor.cliente
                        orcamento_db.valor_mao_de_obra = valor_mo_final
                        orcamento_db.valor_pecas = total_pecas
                        orcamento_db.valor_total = total_geral
                        orcamento_db.observacoes = self.txt_obs.value
                        session.add(orcamento_db)
                        session.commit()
                        
                        itens_antigos = session.exec(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == self.editando_orcamento_id)).all()
                        for item in itens_antigos: session.delete(item)
                        session.commit()
                    orcamento_id_vinculo = self.editando_orcamento_id
                else:
                    novo_orcamento = Orcamento(
                        motor_id=motor.id, motor_descricao=f"{motor.marca} {motor.tipo} ({motor.cv}CV)",
                        cliente_nome=motor.cliente, valor_mao_de_obra=valor_mo_final, valor_pecas=total_pecas,
                        valor_total=total_geral, observacoes=self.txt_obs.value, status="Pendente"
                    )
                    session.add(novo_orcamento)
                    session.commit()
                    session.refresh(novo_orcamento)
                    orcamento_id_vinculo = novo_orcamento.id
                
                for item in self.itens_temporarios_pecas:
                    item_db = ItemOrcamento(
                        orcamento_id=orcamento_id_vinculo, descricao=item["nome"], quantidade=item["qtd"],
                        preco_unitario=item["preco_uni"], preco_total=item["total"]
                    )
                    session.add(item_db)
                session.commit()
                
            self.editando_orcamento_id = None
            self.itens_temporarios_pecas.clear()
            self.txt_valor_mo.value = "0.00"
            self.txt_obs.value = ""
            self.drop_motores.value = None
            self.txt_detalhes_motor.value = "Selecione um motor para exibir os detalhes."
            self.txt_detalhes_motor.color = ft.Colors.GREY_400
            self.btn_salvar.text = "Salvar e Emitir Orçamento"
            self.btn_salvar.bgcolor = ft.Colors.GREEN_700
            self.btn_cancelar_edicao.visible = False
            
            self.atualizar_totais_tela()
            self.txt_detalhes_motor.value = "✅ Orçamento guardado e emitido!"
            self.txt_detalhes_motor.color = ft.Colors.GREEN_400
            self.pg.update()
            
        except Exception as ex:
            self.txt_detalhes_motor.value = f"❌ Erro na operação: {str(ex)}"
            self.txt_detalhes_motor.color = ft.Colors.RED_400
            self.pg.update()
            