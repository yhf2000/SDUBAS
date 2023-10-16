from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, TEXT, create_engine, func, Index
from model.db import Base

class Resource(Base):  # 资源表
    __tablename__ = "resource"
    __table_args__ = (
        Index('ix_resource_Id', "Id"),  # 非唯一的索引
        Index('ix_resource_Id_has_delete', "Id", "has_delete"),  # 非唯一的索引
    )
    Id = Column(Integer, primary_key=True, unique=True)  # 主键
    name = Column(String(64), nullable=False)  # 名字
    count = Column(Integer, nullable=False)  # 数目
    state = Column(Integer, nullable=False)  # 状态是否可用，1可用，0不可用
    has_delete = Column(Integer, nullable=False, default=0)  # 是否删除


class Financial(Base):  # 资金表
    __tablename__ = "financial"
    __table_args__ = (
        Index('ix_financial_Id', "Id"),  # 非唯一的索引
        Index('ix_financial_Id_has_delete', "Id", "has_delete"),  # 非唯一的索引
    )
    Id = Column(Integer, primary_key=True)  # 主键
    name = Column(String(64), nullable=False)  # 名称
    note = Column(TEXT, nullable=False)  # 备注
    create_dt = Column(DateTime, nullable=False, default=func.now())  # 创建时间自动填入
    has_delete = Column(Integer, nullable=False, default=0)  # 是否删除
    children = relationship("Bill")  # 一对多


class Bill(Base):  # 流水表
    __tablename__ = "amount"
    __table_args__ = (
        Index('ix_Bill_Id', "Id"),  # 非唯一的索引
        Index('ix_Bill_Id_has_delete', "Id", "has_delete"),  # 非唯一的索引
        Index('ix_Bill_Id_state_has_delete', "Id", "state", "has_delete"),  # 非唯一的索引
    )
    Id = Column(Integer, primary_key=True)  # 主键
    finance_id = Column(Integer, ForeignKey('financial.Id'), nullable=False)  # 外键，资金项目ID
    state = Column(Integer, nullable=False)  # 状态输入支出0，1
    amount = Column(Integer, nullable=False)  # 数目
    log_content = Column(String(64), nullable=False)  # 日志
    log_file_id = Column(Integer, nullable=True)  # 上传凭证文件id，外键（需要增加）
    has_delete = Column(Integer, nullable=False, default=0)  # 是否删除，自动填入0
    oper_dt = Column(DateTime, nullable=False, default=func.now())  # 操作时间自动填入
