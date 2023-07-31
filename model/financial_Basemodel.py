from typing import List
import time
from pydantic import BaseModel, Field, validator, constr, ConfigDict, BaseConfig
from datetime import datetime
from typing import get_type_hints


class Financial_Basemodel(BaseModel):
    Id: int
    name: str
    note: str
    create_dt: int
    has_delete: int

    class Config:
        from_attributes = True


# 将DateTime转换为时间戳


class ResourceAdd(BaseModel):  # 资源添加请求体
    Id: int = None
    name: constr(strip_whitespace=True, min_length=1)  # 字符串类型的字段，去除首尾空格，最小长度为1
    count: int = Field(..., gt=0)  # 整数类型的字段，必须大于0
    state: int = 1  # 是否可用，这部分不确定，应该自动填入1


class ResourceDelete(BaseModel):
    id: int = Field(..., gt=0)  # 整数类型的字段，必须大于0


class FinancialUpdate(BaseModel):  # 修改note时输入，可添加过滤条件
    note: str  # 输入即可


class FinancialAdd(BaseModel):  # 添加资金项目填入
    Id: int = None  # 整数类型的字段，默认为None
    name: str = Field(..., strip_whitespace=True, min_length=1)  # 字符串类型的字段，不能全为空格，长度至少为1
    note: str = None  # 文本类型的字段，默认为None


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
    id: int = Field(..., gt=0)
    count: int = Field(..., gt=0)
    begintime: datetime
    endtime: datetime


class Bill_basemodel(BaseModel):
    Id: int
    finance_id: int
    state: int
    amount: int
    log_content: str
    log_file_id: int
    has_delete: int
    oper_dt: int

    class Config:
        from_attributes = True
