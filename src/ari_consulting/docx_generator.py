"""Gerador DOCX autoral e neutro baseado apenas no núcleo público."""

from decimal import Decimal
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from .models import Briefing, Mode
from .pipeline import process_briefing


def _money(value: Decimal) -> str:
    rendered = f"{value:,.2f}"
    return "R$ " + rendered.replace(",", "X").replace(".", ",").replace("X", ".")


def _paragraph(text: str, style: str | None = None, bold: bool = False) -> str:
    properties = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    run_properties = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return f'<w:p>{properties}<w:r>{run_properties}<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def _cell(text: str, bold: bool = False, shade: str | None = None) -> str:
    shading = f'<w:shd w:fill="{shade}"/>' if shade else ""
    return f'<w:tc><w:tcPr>{shading}<w:vAlign w:val="center"/></w:tcPr>{_paragraph(text, bold=bold)}</w:tc>'


def _row(values: tuple[str, ...], header: bool = False, alternate: bool = False) -> str:
    shade = "D9E2F3" if header else ("F2F2F2" if alternate else None)
    return "<w:tr>" + "".join(_cell(value, bold=header, shade=shade) for value in values) + "</w:tr>"


def _services_table(briefing: Briefing) -> str:
    rows = [_row(("Serviço", "Quantidade", "Valor unitário", "Subtotal"), header=True)]
    for index, item in enumerate(briefing.services):
        rows.append(_row((item.name, str(item.quantity), _money(item.unit_price), _money(item.unit_price * item.quantity)), alternate=index % 2 == 1))
    borders = "".join(f'<w:{edge} w:val="single" w:sz="4" w:color="D9D9D9"/>' for edge in ("top", "left", "bottom", "right", "insideH", "insideV"))
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in (3900, 1200, 1700, 1700))
    return f'<w:tbl><w:tblPr><w:tblW w:w="8500" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(rows)}</w:tbl>'


def _document_xml(briefing: Briefing) -> str:
    summary = process_briefing(briefing)
    body = [
        _paragraph("Documento demonstrativo", style="Title"),
        _paragraph(summary.label, bold=True),
        _paragraph("Este documento apresenta exclusivamente dados fictícios para demonstrar o fluxo local do sistema."),
        _paragraph("Identificação fictícia", style="Heading1"),
        _paragraph(f"Cliente: {summary.customer_name}"),
        _paragraph(f"E-mail: {summary.contact_email}"),
        _paragraph(f"Referência: {summary.proposal_reference}"),
        _paragraph("Resumo executivo", style="Heading1"),
        _paragraph(f"A demonstração reúne {summary.service_count} item(ns), com subtotal de {_money(summary.subtotal)}, desconto de {summary.discount_percent}% e total calculado de {_money(summary.total)}."),
        _paragraph("Itens e valores", style="Heading1"),
        _services_table(briefing),
        _paragraph("Totais", style="Heading1"),
        _paragraph(f"Subtotal: {_money(summary.subtotal)}"),
        _paragraph(f"Desconto: {summary.discount_percent}% ({_money(summary.discount_amount)})"),
        _paragraph(f"Total calculado pelo sistema: {_money(summary.total)}", bold=True),
        _paragraph("Observação", style="Heading1"),
        _paragraph("Todos os nomes, contatos, serviços e valores deste arquivo são exclusivamente demonstrativos."),
    ]
    section = '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + "".join(body) + section + "</w:body></w:document>"


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""

DOCUMENT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:spacing w:after="140" w:line="276" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="280"/></w:pPr><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="36"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="280" w:after="120"/></w:pPr><w:rPr><w:b/><w:color w:val="000000"/><w:sz w:val="26"/></w:rPr></w:style>
</w:styles>"""


def generate_demo_docx(briefing: Briefing, destination: str | Path) -> Path:
    """Valida um briefing de teste e grava um DOCX demonstrativo do zero."""
    if briefing.mode is not Mode.TEST:
        raise ValueError("o gerador demonstrativo aceita somente MODO TESTE")
    document_xml = _document_xml(briefing)
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as package:
        package.writestr("[Content_Types].xml", CONTENT_TYPES)
        package.writestr("_rels/.rels", ROOT_RELS)
        package.writestr("word/document.xml", document_xml)
        package.writestr("word/styles.xml", STYLES)
        package.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS)
    return output
