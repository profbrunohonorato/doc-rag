import csv
import io
import json
from pathlib import Path
from pypdf import PdfReader
from docx import Document

from Domain.enums import SUPPORTED_EXTENSIONS


class DocumentReader:
    def read(self, path: Path) -> list[tuple[int, str]]:
        suffix = path.suffix.lower()
        if suffix == '.pdf':
            reader = PdfReader(path)
            if reader.is_encrypted:
                raise ValueError('PDF protegido por senha não suportado')
            return [(i + 1, page.extract_text() or '') for i, page in enumerate(reader.pages)]
        if suffix == '.docx':
            document = Document(path)
            text = '\n'.join(p.text for p in document.paragraphs)
            text += '\n' + '\n'.join(' | '.join(c.text for c in row.cells)
                                     for table in document.tables for row in table.rows)
            return [(1, text)]
        text = path.read_text(encoding='utf-8-sig')
        if suffix == '.json':
            text = json.dumps(json.loads(text), ensure_ascii=False, indent=2)
        elif suffix == '.csv':
            rows = csv.DictReader(io.StringIO(text))
            text = '\n'.join(json.dumps(row, ensure_ascii=False) for row in rows)
        elif suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError('Formato não suportado')
        return [(1, text)]
