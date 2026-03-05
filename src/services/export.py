import csv
import io
import json
from datetime import datetime


def export_to_csv(columns: list, rows: list, filename: str = None) -> tuple:
    """
    Gera um arquivo CSV a partir dos dados.
    Returns: (csv_content_bytes, filename)
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        writer.writerow(row)

    csv_content = output.getvalue().encode('utf-8-sig')  # BOM para Excel
    if not filename:
        filename = f"wanda_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return csv_content, filename


def export_to_pdf(columns: list, rows: list, title: str = "Relatório Wanda", sql: str = None) -> tuple:
    """
    Gera um PDF com os dados da consulta.
    Returns: (pdf_bytes, filename)
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buffer = io.BytesIO()
    page_size = landscape(A4) if len(columns) > 5 else A4
    doc = SimpleDocTemplate(buffer, pagesize=page_size, topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=16, textColor=colors.HexColor('#6C3CE1'), alignment=TA_CENTER)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    sql_style = ParagraphStyle('SQL', parent=styles['Code'], fontSize=7, textColor=colors.HexColor('#444'), backColor=colors.HexColor('#f5f5f5'))

    story = []

    # Cabeçalho
    story.append(Paragraph("🔮 Wanda", title_style))
    story.append(Paragraph(title, ParagraphStyle('T2', parent=styles['Heading2'], alignment=TA_CENTER)))
    story.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", subtitle_style))
    story.append(Spacer(1, 0.5*cm))

    if sql:
        story.append(Paragraph(f"SQL: {sql[:300]}{'...' if len(sql) > 300 else ''}", sql_style))
        story.append(Spacer(1, 0.3*cm))

    # Tabela de dados
    max_rows = 500
    data = [columns] + rows[:max_rows]

    col_width = (page_size[0] - 3*cm) / max(len(columns), 1)
    col_widths = [col_width] * len(columns)

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6C3CE1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0ecff')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(table)

    if len(rows) > max_rows:
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f"* Exibindo {max_rows} de {len(rows)} linhas.", subtitle_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    filename = f"wanda_relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    return pdf_bytes, filename
