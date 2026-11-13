import os
import uuid
import pytest
from sqlalchemy import delete
from Domain.document_model import Answer, AuditEvent
from Infra.Data.db_context import DbContext
from Infra.Data.repositories.document_repository import DocumentRepository


@pytest.mark.skipif(not os.environ.get('TEST_DATABASE_URL'), reason='Requer PostgreSQL descartável')
def test_postgres_transaction_review_and_audit():
    db = DbContext(os.environ['TEST_DATABASE_URL'])
    db.initialize()
    repo = DocumentRepository(db)
    answer_id = str(uuid.uuid4())
    try:
        repo.save_answer(dict(id=answer_id, question='Teste fictício', answer='Resposta [1]',
                             sources=[], status='pending', model='fake', duration_ms=1))
        assert repo.review(answer_id, 'approved', 'Ana', 'Conferido')['status'] == 'approved'
        with pytest.raises(ValueError):
            repo.review(answer_id, 'rejected', 'Outro', '')
        with pytest.raises(KeyError):
            repo.review(str(uuid.uuid4()), 'approved', 'Ana', '')
        assert any(event['entity_id'] == answer_id and event['action'] == 'answer.approved'
                   for event in repo.audit())
    finally:
        with db.create_session.begin() as session:
            session.execute(delete(AuditEvent).where(AuditEvent.entity_id == answer_id))
            session.execute(delete(Answer).where(Answer.id == answer_id))
        db.dispose()
