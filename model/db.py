from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import declarative_base

from const import SQLALCHEMY_DATABASE_URL
import redis
pool1 = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1, encoding='UTF-8')
pool2 = redis.ConnectionPool(host='127.0.0.1', port=6379, db=2, encoding='UTF-8')
session_db = redis.Redis(connection_pool=pool1)  # 根据token缓存有效session
user_information_db = redis.Redis(connection_pool=pool2)  # 根据token缓存用户基本信息

Base = declarative_base()


class dbSession:
    def __init__(self, db_url=SQLALCHEMY_DATABASE_URL):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.SessionThreadLocal = scoped_session(self.SessionLocal)


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
