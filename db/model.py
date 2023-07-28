import copy
import json
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, TEXT, create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

link = "mysql+pymysql://root:123456@127.0.0.1:3306/demo47"

Base = declarative_base()


class Resource(Base):#资源表
    __tablename__ = "resource"
    Id = Column(Integer, primary_key=True, unique=True)#主键
    name = Column(String(64), nullable=False)#名字
    count = Column(Integer, nullable=False)#数目
    state = Column(Integer, nullable=False)#状态是否可用，1可用，0不可用
    has_delete = Column(Integer, nullable=False, default=0)#是否删除


class Financial(Base):#资金表
    __tablename__ = "financial"
    Id = Column(Integer, primary_key=True)#主键
    name = Column(String(64), nullable=False)#名称
    note = Column(TEXT, nullable=False)#备注
    create_dt = Column(DateTime, nullable=False, default=func.now())#创建时间自动填入
    has_delete = Column(Integer, nullable=False, default=0)#是否删除
    children = relationship("Bill")#一对多


class Bill(Base):#流水表
    __tablename__ = "amount"
    Id = Column(Integer, primary_key=True)#主键
    finance_id = Column(Integer, ForeignKey('financial.Id'), nullable=False)#外键，资金项目ID
    state = Column(Integer, nullable=False)#状态输入支出0，1
    amount = Column(Integer, nullable=False)#数目
    log_content = Column(String(64), nullable=False)#日志
    log_file_id = Column(Integer, nullable=True)#上传凭证文件id，外键（需要增加）
    has_delete = Column(Integer, nullable=False, default= 0)#是否删除，自动填入0
    oper_dt = Column(DateTime, nullable=False, default=func.now())#操作时间自动填入


class dbSession:
    session = None

    def __init__(self):
        engine = create_engine(
            link,
            echo=True
        )
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def getSession(self):
        return self.session

    def jsonDumps(self, data, keys):
        for key in keys:
            if key in data and data[key] is not None:
                data[key] = json.dumps(data[key])
        return data

    def jsonLoads(self, data, keys):
        for key in keys:
            if key in data and data[key] is not None:
                data[key] = json.loads(data[key])
        return data

    # 待处理的查出数据，要转换的时间数据，要删除的数据
    def dealData(self, data, timeKeys=None, popKeys=None):
        from utils.times import getMsTime
        dict_: dict = copy.deepcopy(data.__dict__)
        dict_.pop("_sa_instance_state")
        if popKeys is not None:
            for key in popKeys:
                if key in dict_:
                    dict_.pop(key)
        if timeKeys is not None:
            for key in timeKeys:
                if key in dict_ and dict_[key] is not None:
                    dict_[key] = getMsTime(dict_[key])
        return dict_

    def dealDataToy(self, data, timeKeys=None, saveKeys=None):
        from utils.times import getMsTime
        dict_: dict = copy.deepcopy(data.__dict__)
        dict_.pop("_sa_instance_state")
        if saveKeys is not None:
            ls = []
            for key in dict_:
                if key not in saveKeys:
                    ls.append(key)
            for x in ls:
                dict_.pop(x)
        if timeKeys is not None:
            for key in timeKeys:
                if key in dict_ and dict_[key] is not None:
                    dict_[key] = getMsTime(dict_[key])
        return dict_

    def deleteNone(self, data):
        if type(data) == list:
            for i in range(len(data)):
                data[i] = self.deleteNone(data[i])
        elif type(data) == dict:
            data = {key: value for key, value in data.items() if
                    value is not None}

        return data

    def dealDataList(self, data, timeKeys=None, popKeys=None):
        dicts = []
        for d in data:
            dicts.append(self.dealData(d, timeKeys, popKeys))
        return dicts

    def __del__(self):
        self.session.close()
