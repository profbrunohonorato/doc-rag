import hashlib
import logging
from Application.helpers.chunk_helper import split_text
from Application.interfaces.i_ai_provider import IAIProvider
from Application.interfaces.i_vector_store import IVectorStore
from Application.interfaces.i_document_reader import IDocumentReader
from Domain.interfaces.i_document_repository import IDocumentRepository
from Domain.enums import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, settings, repository: IDocumentRepository, reader: IDocumentReader,
                 ai: IAIProvider, vectors: IVectorStore, lock):
        self.settings, self.repository, self.reader = settings, repository, reader
        self.ai, self.vectors, self.lock = ai, vectors, lock

    def scan(self):
        root = self.settings.documents_path.resolve()
        if not root.is_dir():
            raise ValueError('Pasta de documentos inexistente')
        with self.lock:
            seen = set()
            for path in sorted(root.rglob('*')):
                if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                    continue
                if path.is_symlink() or not path.resolve().is_relative_to(root):
                    continue
                name = path.relative_to(root).as_posix()
                document_id = hashlib.sha256(name.encode()).hexdigest()
                seen.add(document_id)
                previous = self.repository.document(document_id)
                try:
                    if path.stat().st_size > self.settings.max_file_bytes:
                        raise ValueError('Arquivo excede o limite configurado')
                    content = path.read_bytes()
                    config = f'{self.settings.embedding_model}:{self.settings.chunk_size}:{self.settings.chunk_overlap}'
                    checksum = hashlib.sha256(content + config.encode()).hexdigest()
                    if previous and previous['checksum'] == checksum and previous['status'] == 'indexed':
                        continue
                    self.repository.save_document(document_id, name=name, status='indexing', error=None)
                    chunks = [dict(name=name, page=page, text=part)
                              for page, text in self.reader.read(path)
                              for part in split_text(text, self.settings.chunk_size, self.settings.chunk_overlap)]
                    if not chunks:
                        raise ValueError('Documento sem texto extraível; PDFs digitalizados precisam de OCR externo')
                    embeddings = []
                    for start in range(0, len(chunks), 16):
                        embeddings.extend(self.ai.embed([c['text'] for c in chunks[start:start + 16]]))
                    self.vectors.replace(document_id, chunks, embeddings)
                    self.repository.save_document(document_id, name=name, checksum=checksum,
                                                  status='indexed', chunks=len(chunks), error=None)
                except Exception as exc:
                    # Falha invalida também versões antigas, evitando servir texto obsoleto.
                    self.vectors.delete(document_id)
                    logger.warning('ingestion_failed document=%s type=%s', document_id, type(exc).__name__)
                    message = str(exc) if isinstance(exc, ValueError) else 'Falha ao processar; confira os modelos e logs.'
                    self.repository.save_document(document_id, name=name, status='error', chunks=0, error=message)
            for document in self.repository.documents():
                if document['id'] not in seen and document['status'] != 'removed':
                    self.vectors.delete(document['id'])
                    self.repository.save_document(document['id'], status='removed', chunks=0, error=None)
        return self.repository.documents()
