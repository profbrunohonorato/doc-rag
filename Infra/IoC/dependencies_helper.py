from functools import lru_cache
from threading import RLock
from Application.services.ingestion_service import IngestionService
from Application.services.rag_service import RagService
from Infra.Data.db_context import DbContext
from Infra.Data.repositories.document_repository import DocumentRepository
from Infra.External.ai.ollama_provider import OllamaProvider
from Infra.External.documents.document_reader import DocumentReader
from Infra.External.vector.chromadb_vector_store import ChromaDBVectorStore
from Presentation.API.settings import get_settings


class Services:
    def __init__(self):
        settings = get_settings()
        self.db = DbContext(settings.database_url)
        self.repository = DocumentRepository(self.db)
        self.ai = OllamaProvider(settings)
        self.vectors = ChromaDBVectorStore(settings.vector_path, settings.embedding_model)
        lock = RLock()
        self.ingestion = IngestionService(settings, self.repository, DocumentReader(), self.ai, self.vectors, lock)
        self.rag = RagService(settings, self.repository, self.ai, self.vectors, lock)


@lru_cache
def get_services():
    return Services()
