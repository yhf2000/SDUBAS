from typing import List, Optional
import time
from pydantic import BaseModel, Field, validator, constr, ConfigDict, BaseConfig, field_serializer
from datetime import datetime
from typing import get_type_hints
from type.permissions import Add_Role_For_Work_Base
from utils.times import getMsTime


class Resource_Basemodel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    Id: int
    name: str
    count: int
    state: int
    has_delete: int


class Financial_Basemodel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    Id: int
    name: str
    note: str
    create_dt: datetime
    has_delete: int


class Financial_ModelOpt(Financial_Basemodel):
    @field_serializer('create_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class ResourceAdd(BaseModel):  # 资源添加请求体
    Id: int = None
    name: constr(strip_whitespace=True, min_length=1)  # 字符串类型的字段，去除首尾空格，最小长度为1
    count: int = Field(..., gt=0)  # 整数类型的字段，必须大于0
    state: int = 1  # 是否可用，这部分不确定，应该自动填入1
    roles: List[Add_Role_For_Work_Base]


class ResourceDelete(BaseModel):
    id: int = Field(..., gt=0)  # 整数类型的字段，必须大于0


class FinancialUpdate(BaseModel):  # 修改note时输入，可添加过滤条件
    note: str  # 输入即可


class FinancialAdd(BaseModel):  # 添加资金项目填入
    Id: int = None  # 整数类型的字段，默认为None
    name: str = Field(..., strip_whitespace=True, min_length=1)  # 字符串类型的字段，不能全为空格，长度至少为1
    note: str = None  # 文本类型的字段，默认为None
    roles: List[Add_Role_For_Work_Base]


class AmountAdd(BaseModel):  # 添加流水填入
    finance_id: int = Field(..., gt=0)  # 非空整数类型的字段，要求大于零，其实可不需要，但是输入处理起来简单，所以尽量输入吧
    state: int = Field(..., ge=0, le=1)  # 整数类型的字段，要求为0或1
    amount: int = Field(..., gt=0)  # 整数类型的字段，要求大于零
    log_content: str  # 字符串类型的字段，默认为None
    log_file_id: int = None  # 整数类型的字段，默认为None


class pageRequest(BaseModel):
    pn: int = Field(..., gt=0)
    pg: int = Field(..., gt=0)


class resource_count_update(BaseModel):
    count: int = Field(..., gt=0)


class ApplyBody(BaseModel):
    name: str
    count: int = Field(..., gt=0)
    begintime: str
    endtime: str


class Bill_basemodel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    Id: int
    finance_id: int
    state: int
    amount: int
    log_content: str
    log_file_id: Optional[int]
    has_delete: int
    oper_dt: datetime


class BillModelOpt(Bill_basemodel):
    @field_serializer('oper_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)
