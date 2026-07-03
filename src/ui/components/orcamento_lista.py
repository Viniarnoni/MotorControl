import flet as ft
from src.core.database import get_session
from src.models.entities import Orcamento, ItemOrcamento

class OrcamentoLista(ft.Column):
    def __init__(self, page: ft.Page, on_edit_requested, emitir_whatsapp_callback, emitir_pdf_callback):
        super().__init__(spacing=15, expand=True)
        self.pg = page
        self.on_edit_requested = on_edit_requested
        self.emitir_whatsapp_callback = emitir_whatsapp_callback
        self.emitir_pdf_callback = emitir_pdf_callback

        self.txt_busca = ft.TextField(
            label="Buscar por cliente ou descrição do motor...", expand=True, border_color=ft.Colors.GREY_700,
            on_change=self.filtrar_orcamentos, prefix_icon=ft.Icons.SEARCH
        )
        self.lista_orcamentos_ui = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        self.controls = [
            ft.Text("Histórico de Orçamentos do Sistema", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
            ft.Divider(color=ft.Colors.GREY_800),
            ft.Row([self.txt_busca]),
            ft.Container(content=self.lista_orcamentos_ui, expand=True)
        ]
        
        self.carregar_historico_db()

    def filtrar_orcamentos(self, e):
        self.carregar_historico_db()

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
                                    ft.IconButton(
                                        icon=ft.Icons.CHAT, icon_color=ft.Colors.GREEN_500, tooltip="Enviar via WhatsApp",
                                        on_click=lambda e, oid=o.id, nome=o.cliente_nome: self.emitir_whatsapp_callback(oid, nome)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.PRINT, icon_color=ft.Colors.GREEN_400, tooltip="Gerar PDF / Imprimir",
                                        on_click=lambda e, oid=o.id: self.emitir_pdf_callback(oid)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.CREATE, icon_color=ft.Colors.BLUE_400, tooltip="Editar Orçamento",
                                        on_click=lambda e, oid=o.id: self.on_edit_requested(oid)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, tooltip="Excluir Orçamento",
                                        on_click=lambda e, oid=o.id: self.excluir_orcamento(oid)
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

    def excluir_orcamento(self, orcamento_id):
        def fechar_dialogo_exclusao(e):
            dialogo_exclusao.open = False
            self.pg.update()

        def confirmar_exclusao(e):
            dialogo_exclusao.open = False
            self.pg.update()
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

        dialogo_exclusao = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
            content=ft.Text("Tem certeza que deseja excluir este orçamento? Esta ação não pode ser desfeita."),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo_exclusao),
                ft.ElevatedButton("Sim, excluir", on_click=confirmar_exclusao, bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.pg.overlay.append(dialogo_exclusao)
        dialogo_exclusao.open = True
        self.pg.update()
        