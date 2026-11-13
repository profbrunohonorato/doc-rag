import re
import time
import uuid
from Application.interfaces.i_ai_provider import IAIProvider
from Application.interfaces.i_vector_store import IVectorStore
from Domain.interfaces.i_document_repository import IDocumentRepository


class RagService:
    def __init__(self, settings, repository: IDocumentRepository, ai: IAIProvider,
                 vectors: IVectorStore, lock):
        self.settings, self.repository, self.ai = settings, repository, ai
        self.vectors, self.lock = vectors, lock

    def ask(self, question, top_k=4):
        started = time.perf_counter()
        with self.lock:
            sources = self.vectors.search(self.ai.embed([question])[0], top_k)
            sources = [s for s in sources if s['score'] >= self.settings.min_similarity]
            if not sources:
                answer = 'Não encontrei evidências suficientes nos documentos para responder.'
                status = 'insufficient_evidence'
            else:
                answer = self.ai.generate(question, sources)
                citations = [int(c) for c in re.findall(r'\[(\d+)\]', answer)]
                if not citations or any(c < 1 or c > len(sources) for c in citations):
                    answer = 'O modelo não apresentou citações válidas. Consulte as fontes e reformule a pergunta.'
                    status = 'insufficient_evidence'
                else:
                    status = 'pending' if self.settings.require_review else 'generated'
            return self.repository.save_answer(dict(id=str(uuid.uuid4()), question=question, answer=answer,
                sources=sources, status=status, model=self.settings.chat_model,
                duration_ms=int((time.perf_counter() - started) * 1000)))
