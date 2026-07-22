import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from sqlmodel import select
from src.core.database import get_session
from src.core.paths import get_logo_path
from src.models.entities import Orcamento, ItemOrcamento, Motor, Cliente
from src.repositories.config_repo import ConfigRepository

class PDFService:
    @staticmethod
    def _buscar_cliente_por_nome(session, nome_cliente: str):
        if not nome_cliente or not nome_cliente.strip():
            return None
        nome_alvo = nome_cliente.strip().lower()
        for cliente in session.exec(select(Cliente)).all():
            if cliente.nome and cliente.nome.strip().lower() == nome_alvo:
                return cliente
        return None

    @staticmethod
    def _texto_ou_placeholder(valor: str | None, placeholder: str) -> str:
        if not valor:
            return placeholder
        limpo = valor.strip()
        if not limpo or limpo == "000.000.000-00":
            return placeholder
        return limpo

    @staticmethod
    def _nome_arquivo_seguro(nome: str) -> str:
        """Remove caracteres inválidos para nome de arquivo no Windows."""
        limpo = re.sub(r'[<>:"/\\|?*]', "", (nome or "").strip())
        limpo = re.sub(r"\s+", "_", limpo)
        return limpo or "Cliente"

    @staticmethod
    def gerar_pdf(orcamento_id: int) -> str:
        pasta_saida = Path("orcamentos_emitidos")
        pasta_saida.mkdir(exist_ok=True)
        dados_empresa = ConfigRepository.get_company_data()
        
        with get_session() as session:
            orcamento = session.get(Orcamento, orcamento_id)
            if not orcamento:
                raise Exception("Orçamento não localizado no banco de dados.")
            
            motor = session.get(Motor, orcamento.motor_id)
            itens_pecas = session.exec(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)).all()
            cliente = PDFService._buscar_cliente_por_nome(session, orcamento.cliente_nome)

            cliente_nome = orcamento.cliente_nome or "Cliente"
            # Extrai dados do cliente enquanto a sessão está aberta
            cliente_gov_id = cliente.gov_id if cliente else None
            cliente_endereco = cliente.endereco if cliente else None
            cliente_numero = cliente.numero if cliente else None
            cliente_bairro = cliente.bairro if cliente else None
            cliente_cidade = cliente.cidade if cliente else None
            cliente_estado = cliente.estado if cliente else None
            cliente_telefone = cliente.telefone if cliente else None

        data_geracao = datetime.now().strftime("%d-%m-%Y")
        nome_seguro = PDFService._nome_arquivo_seguro(cliente_nome)
        arquivo_pdf = pasta_saida / f"Orcamento_{nome_seguro}_{data_geracao}.pdf"
        if arquivo_pdf.exists():
            arquivo_pdf = pasta_saida / f"Orcamento_{nome_seguro}_{data_geracao}_{orcamento_id}.pdf"
        
        doc = SimpleDocTemplate(
            str(arquivo_pdf), pagesize=A4,
            rightMargin=35, leftMargin=35, topMargin=35, bottomMargin=35
        )
        story = []
        styles = getSampleStyleSheet()
        
        # Cabeçalho centralizado
        estilo_cabecalho_titulo = ParagraphStyle('CabecalhoTitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16, leading=20, alignment=1, spaceAfter=2)
        estilo_cabecalho_texto = ParagraphStyle('CabecalhoTexto', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, alignment=1, spaceAfter=2)
        estilo_cabecalho_endereco = ParagraphStyle('CabecalhoEndereco', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, alignment=1, spaceAfter=0)
        estilo_orcamento = ParagraphStyle('OrcamentoTitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, spaceAfter=15)
        
        estilo_texto = ParagraphStyle('TextoDoc', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
        estilo_negrito = ParagraphStyle('NegritoDoc', parent=estilo_texto, fontName='Helvetica-Bold')
        estilo_tabela_centro = ParagraphStyle('TabCentro', parent=estilo_texto, alignment=1)
        estilo_tabela_dir = ParagraphStyle('TabDir', parent=estilo_texto, alignment=2)
        
        # --- CABEÇALHO (logo + dados da empresa centralizados) ---
        logo_path = get_logo_path()
        if logo_path:
            logo = RLImage(str(logo_path), width=78, height=78)
            logo.hAlign = "CENTER"
            story.append(logo)
            story.append(Spacer(1, 6))

        story.append(Paragraph(dados_empresa["empresa_nome"], estilo_cabecalho_titulo))
        story.append(Paragraph(dados_empresa["empresa_linha_1"], estilo_cabecalho_texto))
        story.append(Paragraph(dados_empresa["empresa_linha_2"], estilo_cabecalho_endereco))

        story.append(Spacer(1, 12))
        story.append(Paragraph("ORÇAMENTO", estilo_orcamento))
        
        # --- DADOS DO CLIENTE ---
        cnpj_cpf = PDFService._texto_ou_placeholder(cliente_gov_id, "________________")
        endereco = PDFService._texto_ou_placeholder(cliente_endereco, "__________________________________")
        numero = PDFService._texto_ou_placeholder(cliente_numero, "____")
        telefone = PDFService._texto_ou_placeholder(cliente_telefone, "________________")
        cidade = PDFService._texto_ou_placeholder(cliente_cidade, "________________")
        bairro = PDFService._texto_ou_placeholder(cliente_bairro, "________________")
        estado = PDFService._texto_ou_placeholder(cliente_estado, "____")

        dados_cliente = [
            [Paragraph(f"<b>Para:</b> {cliente_nome}", estilo_texto), Paragraph(f"<b>CNPJ/CPF:</b> {cnpj_cpf}", estilo_texto), ""],
            [Paragraph(f"<b>Endereço:</b> {endereco}", estilo_texto), Paragraph(f"<b>nº:</b> {numero}", estilo_texto), Paragraph(f"<b>Tel:</b> {telefone}", estilo_texto)],
            [Paragraph(f"<b>Cidade:</b> {cidade}", estilo_texto), Paragraph(f"<b>Bairro:</b> {bairro}", estilo_texto), Paragraph(f"<b>Estado:</b> {estado}", estilo_texto)]
        ]
        tabela_cliente = Table(dados_cliente, colWidths=[240, 140, 145])
        tabela_cliente.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(tabela_cliente)
        story.append(Spacer(1, 15))
        
        # --- TABELA DE ITENS (MÃO DE OBRA E PEÇAS) ---
        dados_tabela_pecas = [
            [
                Paragraph("<b>Quant.:</b>", estilo_texto),
                Paragraph("<b>DESCRIÇÃO</b>", estilo_texto),
                Paragraph("<b>Unitário</b>", estilo_tabela_centro),
                Paragraph("<b>TOTAL</b>", estilo_tabela_centro)
            ]
        ]
        
        valor_rebobinagem = orcamento.valor_rebobinamento or 0.0
        if valor_rebobinagem < 0.01:
            valor_rebobinagem = 0.0

        # 1. BLOCO DE REBOBINAGEM
        if valor_rebobinagem > 0:
            if motor:
                # Modificação: Tudo em uma linha e exibindo RPM no lugar de Polos
                fases_str = f" {motor.fases}" if motor.fases else ""
                marca_str = f" marca: {motor.marca}" if motor.marca else ""
                modelo_pdf = motor.modelo or motor.tipo
                mod_str = f" mod: {modelo_pdf}" if modelo_pdf else ""
                cv_str = f" CV: {motor.cv}" if motor.cv else ""
                rpm_str = f" RPM: {motor.rpm}" if motor.rpm else ""
                
                descricao_completa = f"Rebobinar motor elétrico{fases_str}{marca_str}{mod_str}{cv_str}{rpm_str}"
                
                dados_tabela_pecas.append([
                    Paragraph("1", estilo_texto),
                    Paragraph(descricao_completa, estilo_texto),
                    Paragraph(f"R$ {valor_rebobinagem:.2f}", estilo_tabela_dir),
                    Paragraph(f"R$ {valor_rebobinagem:.2f}", estilo_tabela_dir)
                ])
            else:
                dados_tabela_pecas.append([
                    Paragraph("1", estilo_texto),
                    Paragraph(f"Serviço de Rebobinagem: {orcamento.motor_descricao}", estilo_texto),
                    Paragraph(f"R$ {valor_rebobinagem:.2f}", estilo_tabela_dir),
                    Paragraph(f"R$ {valor_rebobinagem:.2f}", estilo_tabela_dir)
                ])
            
            # Pula uma linha em branco após o bloco de Rebobinagem
            dados_tabela_pecas.append([
                Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto)
            ])

        # 2. BLOCO DE PEÇAS E COMPONENTES
        for item in itens_pecas:
            dados_tabela_pecas.append([
                Paragraph(str(item.quantidade), estilo_texto),
                Paragraph(item.descricao, estilo_texto),
                Paragraph(f"R$ {item.preco_unitario:.2f}", estilo_tabela_dir),
                Paragraph(f"R$ {item.preco_total:.2f}", estilo_tabela_dir)
            ])
            # Pula uma linha em branco após cada peça para manter o espaçamento do modelo
            dados_tabela_pecas.append([
                Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto)
            ])

        # 3. BLOCO EXCLUSIVO DE MÃO DE OBRA GERAL
        if orcamento.valor_mao_de_obra > 0:
            # Modificação: Pega o texto digitado no formulário ou usa um padrão se estiver vazio
            desc_mao_de_obra = orcamento.descricao_mao_de_obra if orcamento.descricao_mao_de_obra else "Mão de Obra Geral / Serviços de Montagem"
            
            dados_tabela_pecas.append([
                Paragraph("", estilo_texto),
                Paragraph(desc_mao_de_obra, estilo_texto),
                Paragraph(f"R$ {orcamento.valor_mao_de_obra:.2f}", estilo_tabela_dir),
                Paragraph(f"R$ {orcamento.valor_mao_de_obra:.2f}", estilo_tabela_dir)
            ])
            # Pula uma linha em branco após a mão de obra
            dados_tabela_pecas.append([
                Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto)
            ])
            
        # Preenche o restante da tabela com linhas vazias até atingir a estrutura fixa visual
        linhas_atuais = len(dados_tabela_pecas)
        for _ in range(max(0, 15 - linhas_atuais)):
            dados_tabela_pecas.append([
                Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto)
            ])

        tabela_pecas = Table(dados_tabela_pecas, colWidths=[50, 295, 90, 90])
        tabela_pecas.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(tabela_pecas)
        story.append(Spacer(1, 20))
        
        # --- RODAPÉ ---
        data_str = datetime.now().strftime("%d/%m/%Y")
        dados_rodape = [
            [
                Paragraph(f"<b>Data:</b> {data_str}", estilo_texto),
                Paragraph("<b>Ass:</b> Felipe Barrere Arnoni", estilo_tabela_centro),
                Paragraph(f"<b>TOTAL: R$: {orcamento.calcular_total():.2f}</b>", estilo_tabela_dir)
            ]
        ]
        tabela_rodape = Table(dados_rodape, colWidths=[150, 225, 150])
        tabela_rodape.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
        ]))
        story.append(tabela_rodape)
        
        doc.build(story)
        return str(arquivo_pdf.resolve())

    @staticmethod
    def abrir_pdf(caminho: str):
        if sys.platform == "win32":
            os.startfile(caminho)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", caminho])
        else:
            subprocess.Popen(["xdg-open", caminho])

    @staticmethod
    def enviar_whatsapp(caminho_pdf: str, nome_cliente: str, telefone: str = ""):
        """Abre o chat do WhatsApp usando link universal (wa.me) resolvendo telefones vazios."""
        import urllib.parse
        import webbrowser
        from src.models.entities import Cliente

        if not telefone or str(telefone).strip() == "":
            try:
                with get_session() as session:
                    nome_alvo = nome_cliente.strip().lower() if nome_cliente else ""
                    for c in session.exec(select(Cliente)).all():
                        nome_db = c.nome.strip().lower() if c.nome else ""
                        if nome_db == nome_alvo:
                            telefone = c.telefone
                            break
            except Exception:
                pass

        mensagem = f"Olá, {nome_cliente}! Segue o orçamento solicitado."
        mensagem_codificada = urllib.parse.quote(mensagem)
        
        telefone_limpo = "".join(filter(str.isdigit, str(telefone))) if telefone else ""
        
        if telefone_limpo:
            if not telefone_limpo.startswith("55") and len(telefone_limpo) >= 10:
                telefone_limpo = f"55{telefone_limpo}"
            url_whatsapp = f"https://wa.me/{telefone_limpo}?text={mensagem_codificada}"
        else:
            url_whatsapp = f"https://web.whatsapp.com/send?text={mensagem_codificada}"
        
        webbrowser.open(url_whatsapp)
        
        if sys.platform == "win32":
            subprocess.Popen(f'explorer /select,"{Path(caminho_pdf).resolve()}"')
        else:
            os.startfile(Path(caminho_pdf).parent.resolve())
