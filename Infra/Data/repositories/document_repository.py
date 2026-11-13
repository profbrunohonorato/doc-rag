from sqlalchemy import select
from Domain.document_model import Document, Answer, AuditEvent, utcnow


def as_dict(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


class DocumentRepository:
    def __init__(self, db):
        self.db = db

    def documents(self):
        with self.db.create_session() as session:
            return [as_dict(x) for x in session.scalars(select(Document).order_by(Document.name))]

    def document(self, document_id):
        with self.db.create_session() as session:
            row = session.get(Document, document_id)
            return as_dict(row) if row else None

    def save_document(self, document_id, **values):
        with self.db.create_session.begin() as session:
            row = session.get(Document, document_id)
            if row is None:
                row = Document(id=document_id)
                session.add(row)
            for key, value in values.items():
                setattr(row, key, value)
            row.updated_at = utcnow()
            if row.status != 'indexing':
                session.add(AuditEvent(entity_id=document_id, action='document.' + row.status,
                                       details={'name': row.name, 'chunks': row.chunks}))

    def save_answer(self, values):
        with self.db.create_session.begin() as session:
            row = Answer(**values)
            session.add(row)
            session.add(AuditEvent(entity_id=row.id, action='answer.created',
                                   details={'model': row.model, 'status': row.status}))
            session.flush()
            return as_dict(row)

    def answers(self, status=None, offset=0):
        query = select(Answer).order_by(Answer.created_at.desc()).offset(offset).limit(100)
        if status:
            query = query.where(Answer.status == status)
        with self.db.create_session() as session:
            return [as_dict(x) for x in session.scalars(query)]

    def review(self, answer_id, decision, reviewer, note):
        with self.db.create_session.begin() as session:
            row = session.scalar(select(Answer).where(Answer.id == answer_id).with_for_update())
            if row is None:
                raise KeyError(answer_id)
            if row.status != 'pending':
                raise ValueError('Esta resposta não está pendente de revisão.')
            row.status = decision
            session.add(AuditEvent(entity_id=answer_id, action='answer.' + decision,
                                   details={'reviewer': reviewer, 'note': note}))
            session.flush()
            return as_dict(row)

    def audit(self, offset=0):
        with self.db.create_session() as session:
            return [as_dict(x) for x in session.scalars(select(AuditEvent)
                    .order_by(AuditEvent.id.desc()).offset(offset).limit(100))]
