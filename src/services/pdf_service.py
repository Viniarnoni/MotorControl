import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from sqlmodel import select
from src.core.database import get_session
from src.models.entities import Orcamento, ItemOrcamento, Motor

class PDFService:
    @staticmethod
    def gerar_pdf(orcamento_id: int) -> str:
        pasta_saida = Path("orcamentos_emitidos")
        pasta_saida.mkdir(exist_ok=True)
        
        arquivo_pdf = pasta_saida / f"Orcamento_{orcamento_id}.pdf"
        
        with get_session() as session:
            orcamento = session.get(Orcamento, orcamento_id)
            if not orcamento:
                raise Exception("Orçamento não localizado no banco de dados.")
            
            motor = session.get(Motor, orcamento.motor_id)
            itens_pecas = session.exec(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)).all()
        
        doc = SimpleDocTemplate(
            str(arquivo_pdf), pagesize=A4,
            rightMargin=35, leftMargin=35, topMargin=35, bottomMargin=35
        )
        story = []
        styles = getSampleStyleSheet()
        
        # AJUSTE FIX: Adicionado 'leading' proporcional ao 'fontSize' para evitar textos sobrepostos
        estilo_cabecalho_titulo = ParagraphStyle('CabecalhoTitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=1, spaceAfter=4)
        estilo_cabecalho_texto = ParagraphStyle('CabecalhoTexto', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, alignment=1, spaceAfter=4)
        estilo_cabecalho_endereco = ParagraphStyle('CabecalhoEndereco', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, alignment=1, spaceAfter=15)
        estilo_orcamento = ParagraphStyle('OrcamentoTitulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, spaceAfter=15)
        
        estilo_texto = ParagraphStyle('TextoDoc', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
        estilo_negrito = ParagraphStyle('NegritoDoc', parent=estilo_texto, fontName='Helvetica-Bold')
        estilo_tabela_centro = ParagraphStyle('TabCentro', parent=estilo_texto, alignment=1)
        estilo_tabela_dir = ParagraphStyle('TabDir', parent=estilo_texto, alignment=2)
        
        # --- CABEÇALHO ---
        story.append(Paragraph("ELETRORECUPERADORA", estilo_cabecalho_titulo))
        story.append(Paragraph("FELIPE BARRERE ARNONI-MEI CNPJ: 35.032.089/0001-52   Tel:(16) 3252-6033/(16) 98131-5311", estilo_cabecalho_texto))
        story.append(Paragraph("Rua: Ennes Reis Rodrigues, 113 - Jardim Bela Vista - CEP:  15905-004 - Taquaritinga-SP", estilo_cabecalho_endereco))
        
        story.append(Paragraph("ORÇAMENTO", estilo_orcamento))
        
        # --- DADOS DO CLIENTE ---
        dados_cliente = [
            [Paragraph(f"<b>Para:</b> {orcamento.cliente_nome}", estilo_texto), Paragraph("<b>CNPJ:</b> ________________", estilo_texto), ""],
            [Paragraph("<b>Endereço:</b> __________________________________", estilo_texto), Paragraph("<b>nº:</b> ____", estilo_texto), Paragraph("<b>Tel:</b> ________________", estilo_texto)],
            [Paragraph("<b>Cidade:</b> Taquaritinga", estilo_texto), Paragraph("<b>Bairro:</b> Centro", estilo_texto), Paragraph("<b>Estado:</b> São Paulo", estilo_texto)]
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
        
        if orcamento.valor_mao_de_obra > 0:
            if motor:
                linha1_desc = f"Rebobinar motor elétrico {motor.fases if motor.fases else ''} marca: {motor.marca}"
                linha2_desc = f"mod: {motor.tipo} CV: {motor.cv} RPM/Pólos: {motor.polos}"
                
                dados_tabela_pecas.append([
                    Paragraph("1", estilo_texto),
                    Paragraph(linha1_desc, estilo_texto),
                    Paragraph(f"R$ {orcamento.valor_mao_de_obra:.2f}", estilo_tabela_dir),
                    Paragraph(f"R$ {orcamento.valor_mao_de_obra:.2f}", estilo_tabela_dir)
                ])
                dados_tabela_pecas.append([
                    Paragraph("", estilo_texto), Paragraph(linha2_desc, estilo_texto), Paragraph("", estilo_texto), Paragraph("", estilo_texto)
                ])
            else:
                dados_tabela_pecas.append([
                    Paragraph("1", estilo_texto),
                    Paragraph(f"Serviço de Mão de Obra / Manutenção: {orcamento.motor_descricao}", estilo_texto),
                    Paragraph(f"R$ {orcamento.valor_mao_de_obra:.2f}", estilo_tabela_dir),
                    Paragraph(f"R$ {orcamento.valor_mao_de_obra:.2f}", estilo_tabela_dir)
                ])

        for item in itens_pecas:
            dados_tabela_pecas.append([
                Paragraph(str(item.quantidade), estilo_texto),
                Paragraph(item.descricao, estilo_texto),
                Paragraph(f"R$ {item.preco_unitario:.2f}", estilo_tabela_dir),
                Paragraph(f"R$ {item.preco_total:.2f}", estilo_tabela_dir)
            ])
            
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
                Paragraph(f"<b>TOTAL: R$: {orcamento.valor_total:.2f}</b>", estilo_tabela_dir)
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

        print(f"\n--- INÍCIO DO DEBUG WHATSAPP ---")
        print(f"Nome do cliente recebido do orçamento: '{nome_cliente}'")
        print(f"Telefone recebido direto da tela: '{telefone}'")

        # BUSCA AUTOMÁTICA SE VIER VAZIO
        if not telefone or str(telefone).strip() == "":
            print(f"Telefone vazio! Iniciando varredura no banco de dados...")
            try:
                with get_session() as session:
                    todos_clientes = session.exec(select(Cliente)).all()
                    print(f"Total de clientes cadastrados no banco: {len(todos_clientes)}")
                    
                    nome_alvo = nome_cliente.strip().lower() if nome_cliente else ""
                    
                    for c in todos_clientes:
                        nome_db = c.nome.strip().lower() if c.nome else ""
                        print(f" -> Comparando banco: '{nome_db}' (Tel: {c.telefone}) com alvo: '{nome_alvo}'")
                        
                        if nome_db == nome_alvo:
                            telefone = c.telefone
                            print(f" [!] MATCH ENCONTRADO! O telefone agora é: '{telefone}'")
                            break
            except Exception as db_ex:
                print(f"ERRO DE BANCO DE DADOS DURANTE A BUSCA: {db_ex}")

        print(f"Telefone final processado antes de gerar o link: '{telefone}'")

        mensagem = f"Olá, {nome_cliente}! Segue o orçamento do serviço da Eletrorecuperadora. 🛠️⚡"
        mensagem_codificada = urllib.parse.quote(mensagem)
        
        telefone_limpo = "".join(filter(str.isdigit, str(telefone))) if telefone else ""
        
        if telefone_limpo:
            if not telefone_limpo.startswith("55") and len(telefone_limpo) >= 10:
                telefone_limpo = f"55{telefone_limpo}"
            
            print(f"URL gerada: https://wa.me/{telefone_limpo}")
            url_whatsapp = f"https://wa.me/{telefone_limpo}?text={mensagem_codificada}"
        else:
            print("Nenhum telefone encontrado. Abrindo WhatsApp Web Geral...")
            url_whatsapp = f"https://web.whatsapp.com/send?text={mensagem_codificada}"
            
        print(f"--- FIM DO DEBUG WHATSAPP ---\n")
        
        webbrowser.open(url_whatsapp)
        
        if sys.platform == "win32":
            import subprocess
            subprocess.Popen(f'explorer /select,"{Path(caminho_pdf).resolve()}"')
        else:
            os.startfile(Path(caminho_pdf).parent.resolve())
