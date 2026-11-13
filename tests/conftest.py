from threading import RLock
import pytest
from Presentation.API.settings import Settings
from Infra.Data.db_context import DbContext
from Infra.Data.repositories.document_repository import DocumentRepository
from Infra.External.documents.document_reader import DocumentReader
from Infra.External.vector.chromadb_vector_store import ChromaDBVectorStore
from Application.services.ingestion_service import IngestionService
from Application.services.rag_service import RagService


class FakeAI:
    calls = 0
    fail = False
    response = 'São necessários CPF e documento de identificação [1].'

    def embed(self, texts):
        self.calls += 1
        if self.fail:
            raise RuntimeError('offline')
        return [[1.0, 0.0, 0.0] if 'conta' in text.lower() or 'cpf' in text.lower()
                else [0.0, 1.0, 0.0] for text in texts]

    def generate(self, question, sources):
        return self.response

    def ready(self):
        return True

    def close(self):
        pass


@pytest.fixture
def stack(tmp_path):
    from types import SimpleNamespace
    root = tmp_path / 'documents'
    root.mkdir()
    settings = Settings(_env_file=None, documents_path=root, database_url=f'sqlite:///{tmp_path}/test.db',
                        vector_path=str(tmp_path / 'vectors'))
    db = DbContext(settings.database_url)
    db.initialize()
    repository = DocumentRepository(db)
    ai = FakeAI()
    vectors = ChromaDBVectorStore(settings.vector_path, settings.embedding_model)
    lock = RLock()
    services = SimpleNamespace(db=db, repository=repository, ai=ai, vectors=vectors)
    services.ingestion = IngestionService(settings, repository, DocumentReader(), ai, vectors, lock)
    services.rag = RagService(settings, repository, ai, vectors, lock)
    yield settings, services
    db.dispose()
