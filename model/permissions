import json
import copy

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql

link = "mysql+pymysql://root:318253shimima@localhost:3306/sdubas"
Base = declarative_base()

engine = create_engine(link, echo=True)


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, nullable=False, unique=True)  # 主键
    name = Column(String(255), nullable=False, unique=True)  # 角色名称
    description = Column(String(255), nullable=False)  # 角色描述
    superiorId = Column(Integer, nullable=False, index=True)  # 角色的上级角色
    template = Column(Integer, nullable=False, index=True)  # 是否为模板角色
    template_val = Column(String(4096))  # 记录模板配置内容的 json 字符串
    tplt_id = Column(Integer, index=True)  # base模板角色id，外键
    status = Column(Integer, nullable=False, index=True)
    # 角色状态
    # 0 可用
    # 1 申请中
    # 2 申请被拒
    # 3 停用
    superiorListId = Column(String(4096))  # 父节点列表JSON
    has_delete = Column(Integer, nullable=False, index=True)  # 是否已经删除


class Privilege(Base):
    __tablename__ = "work-role"

    # 定义字段
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False, index=True)  # 外键关联 role 表的 id 字段
    roles_alias = Column(String(64))  # 业务内角色的别名
    service_type = Column(Integer, nullable=False, index=True)  # 业务类型 0: 用户 1：学校 2：班级 3：资源 4：资金
    service_id = Column(Integer, index=True)  # 业务id，Null 代表整个业务
    type = Column(String(64), index=True)  # 角色类型
    has_delete = Column(Integer, nullable=False, index=True)  # 是否已经删除


class Privilege(Base):
    __tablename__ = "privilege"

    # 定义字段
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    service_type = Column(Integer, nullable=False, index=True)  # 业务类型 0: 用户, 1: 学校, 2: 班级, 3: 资源, 4: 资金
    service_id = Column(Integer, index=True)  # 业务id，Null 代表整个业务
    key = Column(String(64), index=True)  # 权限标识, url 识别
    name = Column(String(64), index=True)  # 权限名称
    name_alias = Column(String(64))  # 角色在业务内的别名
    has_delete = Column(Integer, nullable=False, index=True)  # 是否已经删除


class RolePrivilege(Base):
    __tablename__ = "role_privilege"

    # 定义字段
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False, index=True)  # 外键关联 role 表的 id 字段
    privilege_id = Column(Integer, ForeignKey('privilege.id'), nullable=False, index=True)  # 外键关联 privilege 表的 id 字段
    start_dt = Column(DateTime)  # 时间限制开始时间，没有限制则为 Null
    end_dt = Column(DateTime)  # 时间限制结束时间，没有限制则为 Null
    has_delete = Column(Integer, nullable=False, index=True)  # 是否已经删除


class User(Base):
    __tablename__ = "user"

    # 定义字段
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    username = Column(String(32), nullable=False, unique=True)  # 用户名，最大长度为 32
    password = Column(String(128), nullable=False)  # 密码，最大长度为 128
    email = Column(String(64), nullable=False, unique=True)  # 邮箱地址，最大长度为 64
    card_id = Column(String(32), unique=True)  # 学号或工号，最大长度为 32
    registration_dt = Column(DateTime)  # 注册时间，新建时自动填写
    storage_quota = Column(Integer, nullable=False)  # 存储空间限制（MB）
    status = Column(Integer, nullable=False, index=True)  # 账号状态 0: 正常使用, 1: 账号未激活, 2: 账号已注销, 3: 账号被封禁
    has_delete = Column(Integer, nullable=False, index=True)  # 是否已经删除


class UserRole(Base):
    __tablename__ = "user_role"

    # 定义字段
    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False, index=True)  # 外键关联 role 表的 id 字段
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)  # 外键关联 user 表的 id 字段
    has_delete = Column(Integer, nullable=False, index=True)  # 是否已经删除
