from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from const import SQLALCHEMY_DATABASE_URL


class dbSession:
    def __init__(self, db_url=SQLALCHEMY_DATABASE_URL):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.SessionThreadLocal = scoped_session(self.SessionLocal)

    def init_db(self, base):
        base.metadata.create_all(self.engine)

    @contextmanager
    def get_db(self):
        if self.SessionThreadLocal is None:
            raise Exception("Database not connected")
        session = self.SessionThreadLocal()
        try:
            yield session
        finally:
            session.close()

    def add(self, record):
        with self.get_db() as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.id

    def delete(self, record):
        record_id = record.id
        with self.get_db() as session:
            session.delete(record)
            session.commit()
            return record_id