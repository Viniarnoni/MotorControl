import flet as ft

from src.repositories.config_repo import ConfigRepository


class ConfigView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.campos = {
            "empresa_nome": ft.TextField(label="Nome da Empresa", border_color=ft.Colors.BLUE_400),
            "empresa_cnpj": ft.TextField(label="CNPJ", border_color=ft.Colors.BLUE_400),
            "empresa_telefone": ft.TextField(label="Telefone", border_color=ft.Colors.BLUE_400),
            "empresa_endereco": ft.TextField(label="Endereço", border_color=ft.Colors.BLUE_400),
            "empresa_cep": ft.TextField(label="CEP", border_color=ft.Colors.BLUE_400),
            "empresa_cidade_estado": ft.TextField(label="Cidade / Estado", border_color=ft.Colors.BLUE_400),
            "empresa_linha_1": ft.TextField(
                label="Linha 1 do Cabeçalho",
                multiline=True,
                min_lines=2,
                max_lines=3,
                border_color=ft.Colors.BLUE_400,
            ),
            "empresa_linha_2": ft.TextField(
                label="Linha 2 do Cabeçalho",
                multiline=True,
                min_lines=2,
                max_lines=3,
                border_color=ft.Colors.BLUE_400,
            ),
        }

        self._carregar_dados()

    def _carregar_dados(self):
        dados = ConfigRepository.get_company_data()
        for chave, campo in self.campos.items():
            campo.value = dados.get(chave, "")

    def salvar(self, e):
        ConfigRepository.save_company_data(
            {chave: campo.value.strip() for chave, campo in self.campos.items()}
        )
        self.page.snack_bar = ft.SnackBar(
            ft.Text("Configurações da empresa salvas com sucesso."),
            bgcolor=ft.Colors.GREEN_700,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def build(self):
        return ft.Container(
            expand=True,
            padding=30,
            content=ft.Column(
                [
                    ft.Text("Configurações da Empresa", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Edite os dados usados no cabeçalho do PDF.",
                        color=ft.Colors.GREY_400,
                    ),
                    ft.Divider(height=15, color=ft.Colors.GREY_800),
                    self.campos["empresa_nome"],
                    ft.Row(
                        [self.campos["empresa_cnpj"], self.campos["empresa_telefone"]],
                        spacing=15,
                    ),
                    self.campos["empresa_endereco"],
                    ft.Row(
                        [self.campos["empresa_cep"], self.campos["empresa_cidade_estado"]],
                        spacing=15,
                    ),
                    self.campos["empresa_linha_1"],
                    self.campos["empresa_linha_2"],
                    ft.Row(
                        [
                            ft.Button(
                                "Salvar",
                                icon=ft.Icons.SAVE,
                                bgcolor=ft.Colors.BLUE_700,
                                color=ft.Colors.WHITE,
                                on_click=self.salvar,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
            ),
        )
