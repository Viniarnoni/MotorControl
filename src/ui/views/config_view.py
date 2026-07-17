import shutil
from datetime import datetime

import flet as ft
from src.core.paths import get_backups_dir, get_database_path
from src.repositories.config_repo import ConfigRepository

class ConfigView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True, padding=20)
        self.pg = page

        # --- CAMPOS DE TEXTO ---
        self.txt_nome = ft.TextField(label="Nome da Empresa", expand=True)
        self.txt_linha1 = ft.TextField(label="Documentos / CNPJ / Inscrição", expand=True)
        self.txt_linha2 = ft.TextField(label="Endereço / Contato / Telefone", expand=True)

        # Carrega os dados existentes ao iniciar a tela
        self.carregar_dados()

        # --- LAYOUT VISUAL ---
        self.content = ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.SETTINGS_ROUNDED, color=ft.Colors.BLUE_600, size=30),
                ft.Text("Configurações da Empresa", size=24, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=10, color=ft.Colors.GREY_300),
            ft.Container(height=10),

            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Dados do Cabeçalho do PDF", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                        ft.Container(height=5),
                        
                        ft.Row([self.txt_nome]),
                        ft.Row([self.txt_linha1]),
                        ft.Row([self.txt_linha2]),
                        
                        ft.Container(height=15),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                "Salvar Alterações",
                                icon=ft.Icons.SAVE_ROUNDED,
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE,
                                height=45,
                                on_click=self.salvar_dados
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=15)
                ),
                elevation=2
            ),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Text("Segurança e Backup", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                        ft.Text(
                            "Crie uma cópia do banco de dados atual na pasta de backups do projeto.",
                            color=ft.Colors.GREY_500,
                        ),
                        ft.Row([
                            ft.ElevatedButton(
                                "Gerar Backup do Sistema",
                                icon=ft.Icons.SAVE_ALT,
                                bgcolor=ft.Colors.BLUE_600,
                                color=ft.Colors.WHITE,
                                height=45,
                                on_click=self.gerar_backup
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=15)
                ),
                elevation=2
            )
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def carregar_dados(self):
        """Busca os dados guardados no banco."""
        self.txt_nome.value = ConfigRepository.obter_por_chave("empresa_nome", "ELETRORECUPERADORA PADRÃO LTDA")
        self.txt_linha1.value = ConfigRepository.obter_por_chave("empresa_linha_1", "CNPJ: 00.000.000/0001-00")
        self.txt_linha2.value = ConfigRepository.obter_por_chave("empresa_linha_2", "Rua das Oficinas, 123 - Tel: (00) 0000-0000")

    def salvar_dados(self, e):
        """Salva as alterações."""
        if not self.txt_nome.value.strip():
            self.txt_nome.error_text = "O nome da empresa é obrigatório!"
            self.pg.update()
            return
            
        self.txt_nome.error_text = None
        
        ConfigRepository.salvar_chave("empresa_nome", self.txt_nome.value)
        ConfigRepository.salvar_chave("empresa_linha_1", self.txt_linha1.value)
        ConfigRepository.salvar_chave("empresa_linha_2", self.txt_linha2.value)

        # SnackBar simples de sucesso imune a bugs de versão
        self.pg.snack_bar = ft.SnackBar(ft.Text("✅ Configurações salvas com sucesso!"), bgcolor=ft.Colors.GREEN_700)
        self.pg.snack_bar.open = True
        self.pg.update()

    def gerar_backup(self, e):
        try:
            banco_origem = get_database_path()
            pasta_backup = get_backups_dir()
            pasta_backup.mkdir(exist_ok=True)

            if not banco_origem.exists():
                raise FileNotFoundError("Arquivo do banco de dados não encontrado.")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            arquivo_backup = pasta_backup / f"backup_motorcontrol_{timestamp}.db"
            shutil.copy2(banco_origem, arquivo_backup)

            self.pg.snack_bar = ft.SnackBar(
                ft.Text(f"Backup salvo com sucesso em: {arquivo_backup}"),
                bgcolor=ft.Colors.GREEN_700,
            )
        except Exception as ex:
            self.pg.snack_bar = ft.SnackBar(
                ft.Text(f"Erro ao gerar backup: {ex}"),
                bgcolor=ft.Colors.RED_700,
            )

        self.pg.snack_bar.open = True
        self.pg.update()
