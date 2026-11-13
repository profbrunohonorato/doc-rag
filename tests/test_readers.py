import json
from docx import Document
from pypdf import PdfWriter
from Infra.External.documents.document_reader import DocumentReader


def test_docx_paragraphs_and_tables(tmp_path):
    path = tmp_path / 'document.docx'
    document = Document()
    document.add_paragraph('Abertura de conta')
    document.add_table(rows=1, cols=2).rows[0].cells[0].text = 'CPF'
    document.save(path)
    result = DocumentReader().read(path)
    assert result[0][0] == 1
    assert 'Abertura de conta' in result[0][1] and 'CPF' in result[0][1]


def test_structured_text(tmp_path):
    path = tmp_path / 'document.json'
    path.write_text(json.dumps({'requisito': 'identificação'}), encoding='utf-8')
    assert 'identificação' in DocumentReader().read(path)[0][1]
    path = tmp_path / 'document.csv'
    path.write_text('requisito,prazo\nCPF,2 dias\n', encoding='utf-8')
    assert '"prazo": "2 dias"' in DocumentReader().read(path)[0][1]


def test_pdf_preserves_pages_and_empty_documents_fail_ingestion(tmp_path, stack):
    settings, services = stack
    path = settings.documents_path / 'scan.pdf'
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    writer.write(path)
    assert DocumentReader().read(path) == [(1, ''), (2, '')]
    result = services.ingestion.scan()[0]
    assert result['status'] == 'error'
    assert 'OCR' in result['error']
