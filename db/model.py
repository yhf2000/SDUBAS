from _pydecimal import Decimal
from datetime import datetime
from sqlite3.dbapi2 import Timestamp

from sqlalchemy.orm import relationship
from db.session import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, TEXT


def query_set_to_dict(obj, conv=False):
    """
    Serialize SQLAlchemy Query Set to Dict
    conv: 是否将datetime转换成google.protobuf的Timestamp, true:是，false:否
    """
    obj_dict = {}
    for column in obj.__table__.columns.keys():
        val = getattr(obj, column)
        if isinstance(val, Decimal):
            val = float(val)
        if isinstance(val, datetime):
            if conv:
                x = datetime.now()
                x = x.timestamp()
                val = val.timestamp()
            else:
                val = val.strftime("%Y-%m-%d %H:%M:%S")
        obj_dict[column] = val
    return obj_dict


class Resource(Base):
    __tablename__ = "resource"
    Id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(64), nullable=False)
    count = Column(Integer, nullable=False)
    state = Column(Integer, nullable=False)
    has_delete = Column(Integer, nullable=False)


class Financial(Base):
    __tablename__ = "financial"
    Id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    note = Column(TEXT, nullable=False)
    create_dt = Column(DateTime, nullable=False)
    has_delete = Column(Integer, nullable=False)
    children = relationship("Amount")


class Amount(Base):
    __tablename__ = "amount"
    Id = Column(Integer, primary_key=True)
    finance_id = Column(Integer, ForeignKey('financial.Id'), nullable=False)
    state = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    log_content = Column(String(64), nullable=False)
    log_file_id = Column(Integer, nullable=True)
    has_delete = Column(Integer, nullable=False)
    oper_dt = Column(DateTime, nullable=False)
