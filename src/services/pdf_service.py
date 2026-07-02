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
        # Usa pathlib para criar a pasta de forma compatível com o SO
        pasta_saida = Path("orcamentos_emitidos")
        pasta_saida.mkdir(exist_ok=True)
        
        arquivo_pdf = pasta_saida / f"Orcamento_{orcamento_id}.pdf"
        
        # Coleta os dados diretamente do banco de dados
        with get_session() as session:
            orcamento = session.get(Orcamento, orcamento_id)
            if not orcamento:
                raise Exception("Orçamento não localizado no banco de dados.")
            
            motor = session.get(Motor, orcamento.motor_id)
            itens_pecas = session.exec(select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)).all()
        
        # Configuração da folha A4 com margens limpas (passando string do caminho)
        doc = SimpleDocTemplate(
            str(arquivo_pdf), pagesize=A4,
            rightMargin=35, leftMargin=35, topMargin=35, bottomMargin=35
        )
        story = []
        styles = getSampleStyleSheet()
        
        # Estilos personalizados (Azul Industrial e Cinza)
        estilo_titulo = ParagraphStyle(
            'TituloDoc', parent=styles['Heading1'],
            fontSize=22, leading=26, textColor=colors.HexColor("#1A365D"), spaceAfter=4
        )
        estilo_subtitulo = ParagraphStyle(
            'SubTituloDoc', parent=styles['Heading3'],
            fontSize=10, leading=14, textColor=colors.HexColor("#4A5568"), spaceAfter=15
        )
        estilo_secao = ParagraphStyle(
            'SecaoDoc', parent=styles['Heading2'],
            fontSize=13, leading=16, textColor=colors.HexColor("#2B6CB0"), spaceBefore=12, spaceAfter=6
        )
        estilo_texto = ParagraphStyle(
            'TextoDoc', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#2D3748")
        )
        estilo_negrito = ParagraphStyle(
            'NegritoDoc', parent=estilo_texto, fontName='Helvetica-Bold'
        )
        
        # --- CABEÇALHO ---
        story.append(Paragraph("ORÇAMENTO DE MANUTENÇÃO ELÉTRICA", estilo_titulo))
        data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
        story.append(Paragraph(f"Documento Ref. ID #{orcamento.id} — Emitido em: {data_atual}", estilo_subtitulo))
        story.append(Spacer(1, 5))
        
        # --- BLOCO: DADOS DO CLIENTE E EQUIPAMENTO ---
        story.append(Paragraph("DADOS DO ATENDIMENTO", estilo_secao))
        dados_gerais = [
            [Paragraph("<b>Cliente / Empresa:</b>", estilo_texto), Paragraph(orcamento.cliente_nome, estilo_texto)],
            [Paragraph("<b>Equipamento Principal:</b>", estilo_texto), Paragraph(orcamento.motor_descricao, estilo_texto)]
        ]
        if motor:
            detalhes_motor = f"Tipo: {motor.tipo} | Marca: {motor.marca} | Potência: {motor.cv} CV | Pólos: {motor.polos} | Fases: {motor.fases}"
            dados_gerais.append([Paragraph("<b>Especificações:</b>", estilo_texto), Paragraph(detalhes_motor, estilo_texto)])
            
        tabela_dados = Table(dados_gerais, colWidths=[120, 405])
        tabela_dados.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(tabela_dados)
        story.append(Spacer(1, 10))
        
        # --- BLOCO: RELAÇÃO DE PEÇAS APLICADAS ---
        story.append(Paragraph("RELAÇÃO DE PEÇAS E MATERIAIS", estilo_secao))
        dados_tabela_pecas = [
            [
                Paragraph("<b>Descrição do Componente</b>", estilo_negrito),
                Paragraph("<b>Qtd</b>", estilo_negrito),
                Paragraph("<b>Vlr. Unitário</b>", estilo_negrito),
                Paragraph("<b>Total Item</b>", estilo_negrito)
            ]
        ]
        
        for item in itens_pecas:
            dados_tabela_pecas.append([
                Paragraph(item.descricao, estilo_texto),
                Paragraph(str(item.quantidade), estilo_texto),
                Paragraph(f"R$ {item.preco_unitario:.2f}", estilo_texto),
                Paragraph(f"R$ {item.preco_total:.2f}", estilo_texto)
            ])
            
        if not itens_pecas:
            dados_tabela_pecas.append([Paragraph("Nenhum material cobrado separadamente (Apenas serviços).", estilo_texto), "", "", ""])
            
        tabela_pecas = Table(dados_tabela_pecas, colWidths=[245, 45, 110, 125])
        tabela_pecas.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(tabela_pecas)
        story.append(Spacer(1, 15))
        
        # --- BLOCO: RESUMO FINANCEIRO ---
        story.append(Paragraph("RESUMO DE VALORES", estilo_secao))
        dados_financeiros = [
            [Paragraph("Valor da Mão de Obra / Serviços Técnicos:", estilo_texto), Paragraph(f"R$ {orcamento.valor_mao_de_obra:.2f}", estilo_texto)],
            [Paragraph("Subtotal de Peças Aplicadas:", estilo_texto), Paragraph(f"R$ {orcamento.valor_pecas:.2f}", estilo_texto)],
            [Paragraph("<b>VALOR TOTAL DO ORÇAMENTO:</b>", estilo_negrito), Paragraph(f"<b>R$ {orcamento.valor_total:.2f}</b>", estilo_negrito)]
        ]
        tabela_fin = Table(dados_financeiros, colWidths=[250, 150])
        tabela_fin.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,1), (1,1), 1, colors.HexColor("#1A365D")),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(tabela_fin)
        story.append(Spacer(1, 15))
        
        # --- BLOCO: OBSERVAÇÕES ---
        if orcamento.observacoes and orcamento.observacoes.strip():
            story.append(Paragraph("TERMOS E OBSERVAÇÕES DE COBRANÇA", estilo_secao))
            texto_obs = orcamento.observacoes.replace('\n', '<br/>')
            story.append(Paragraph(texto_obs, estilo_texto))
            story.append(Spacer(1, 20))
            
        # --- CAMPOS DE ASSINATURA ---
        story.append(Spacer(1, 30))
        dados_assinaturas = [
            [
                Paragraph("________________________________________<br/>Responsável Técnico / Oficina", estilo_texto),
                Paragraph("________________________________________<br/>De Acordo / Assinatura do Cliente", estilo_texto)
            ]
        ]
        tabela_ass = Table(dados_assinaturas, colWidths=[260, 260])
        tabela_ass.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(tabela_ass)
        
        # Cria o PDF real
        doc.build(story)
        
        # Retorna o caminho absoluto convertido para string (Usa o formato correto do Windows com \)
        return str(arquivo_pdf.resolve())

    @staticmethod
    def abrir_pdf(caminho: str):
        """Abre o arquivo PDF gerado nativamente usando caminhos absolutos e normalizados."""
        if sys.platform == "win32":
            # os.startfile exige o caminho exato nativo (com \)
            os.startfile(caminho)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", caminho])
        else:
            subprocess.Popen(["xdg-open", caminho])
