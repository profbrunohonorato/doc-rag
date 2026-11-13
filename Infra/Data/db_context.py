from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Domain.document_model import Base


class DbContext:
    def __init__(self, url: str):
        if url.startswith('sqlite:///'):
            Path(url.removeprefix('sqlite:///')).parent.mkdir(parents=True, exist_ok=True)
        options = {'check_same_thread': False} if url.startswith('sqlite') else {}
        self.engine = create_engine(url, pool_pre_ping=True, connect_args=options)
        self.create_session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def initialize(self):
        Base.metadata.create_all(self.engine)

    def dispose(self):
        self.engine.dispose()
