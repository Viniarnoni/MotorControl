import flet as ft
from src.ui.components.orcamento_form import OrcamentoForm
from src.ui.components.orcamento_lista import OrcamentoLista

class OrcamentoView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, padding=20)
        self.pg = page

        # Instancia os componentes filhos passando os callbacks necessários para comunicação
        self.form_component = OrcamentoForm(page=self.pg, on_save_success=self.exibir_popup_sucesso)
        self.lista_component = OrcamentoLista(
            page=self.pg, 
            on_edit_requested=self.mudar_para_edicao,
            emitir_whatsapp_callback=self.emitir_e_enviar_whatsapp,
            emitir_pdf_callback=self.emitir_pdf_orcamento
        )

        # Botões superiores das Abas
        self.btn_aba_novo = ft.ElevatedButton("Novo Orçamento", icon=ft.Icons.ADD_TASK, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, on_click=self.mostrar_aba_novo)
        self.btn_aba_historico = ft.ElevatedButton("Orçamentos Emitidos", icon=ft.Icons.HISTORY, bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, on_click=self.mostrar_aba_historico)
        
        self.botoes_abas = ft.Row([self.btn_aba_novo, self.btn_aba_historico], spacing=10)
        self.area_conteudo = ft.Container(content=self.form_component, expand=True)

        self.content = ft.Column([
            self.botoes_abas,
            ft.Divider(color=ft.Colors.GREY_800, height=2),
            self.area_conteudo
        ], expand=True)

    def mostrar_aba_novo(self, e):
        self.btn_aba_novo.bgcolor = ft.Colors.BLUE_700
        self.btn_aba_historico.bgcolor = ft.Colors.GREY_800
        self.area_conteudo.content = self.form_component
        self.pg.update()

    def mostrar_aba_historico(self, e):
        self.btn_aba_novo.bgcolor = ft.Colors.GREY_800
        self.btn_aba_historico.bgcolor = ft.Colors.BLUE_700
        self.area_conteudo.content = self.lista_component
        self.lista_component.carregar_historico_db()  # Força a atualização ao abrir
        self.pg.update()

    def mudar_para_edicao(self, orcamento_id):
        # Transpõe o ID para o formulário e ativa a aba de edição
        self.form_component.carregar_orcamento_para_edicao(orcamento_id)
        self.mostrar_aba_novo(None)

    def emitir_e_enviar_whatsapp(self, orcamento_id, cliente_nome):
        try:
            from src.services.pdf_service import PDFService
            caminho = PDFService.gerar_pdf(orcamento_id)
            PDFService.enviar_whatsapp(caminho, cliente_nome)
        except Exception as ex:
            print(f"Erro WhatsApp: {ex}")

    def emitir_pdf_orcamento(self, orcamento_id):
        try:
            from src.services.pdf_service import PDFService
            caminho = PDFService.gerar_pdf(orcamento_id)
            PDFService.abrir_pdf(caminho)
        except Exception as ex:
            print(f"Erro PDF: {ex}")

    def exibir_popup_sucesso(self, orcamento_id, nome_cliente):
        def fechar_dialogo_sucesso(ev):
            dialogo_sucesso.open = False
            self.pg.update()

        def abrir_whatsapp_agora(ev):
            dialogo_sucesso.open = False
            self.pg.update()
            self.emitir_e_enviar_whatsapp(orcamento_id, nome_cliente)

        dialogo_sucesso = ft.AlertDialog(
            title=ft.Text("Orçamento Salvo! 🎉", weight=ft.FontWeight.BOLD),
            content=ft.Text(f"O orçamento de {nome_cliente} foi guardado com sucesso. Deseja enviar via WhatsApp agora?"),
            actions=[
                ft.TextButton("Agora não", on_click=fechar_dialogo_sucesso),
                ft.ElevatedButton("Enviar WhatsApp", on_click=abrir_whatsapp_agora, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, icon=ft.Icons.CHAT),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.pg.overlay.append(dialogo_sucesso)
        dialogo_sucesso.open = True
        self.pg.update()
        