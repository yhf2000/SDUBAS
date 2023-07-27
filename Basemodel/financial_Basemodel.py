from datetime import datetime
from pydantic import BaseModel, Field, validator, constr


class ResourceAdd(BaseModel):
    Id: int = None
    name: constr(strip_whitespace=True, min_length=1)  # 字符串类型的字段，去除首尾空格，最小长度为1
    count: int = Field(..., gt=0)  # 整数类型的字段，必须大于0
    state: int = 1
    has_delete: int = 0


class ResourceDelete(BaseModel):
    id: int = Field(..., gt=0)  # 整数类型的字段，必须大于0


class FinancialAdd(BaseModel):
    Id: int = None  # 整数类型的字段，默认为None
    name: str = Field(..., strip_whitespace=True, min_length=1)  # 字符串类型的字段，不能全为空格，长度至少为1
    note: str = None  # 文本类型的字段，默认为None
    create_dt: datetime = None  # 日期时间类型的字段，默认为None
    has_delete: int = 0


class AmountAdd(BaseModel):
    Id: int = None  # 整数类型的字段，默认为None
    finance_id: int = Field(..., gt=0)  # 非空整数类型的字段，要求大于零
    state: int = Field(..., ge=0, le=1)  # 整数类型的字段，要求为0或1
    amount: int = Field(..., gt=0)  # 整数类型的字段，要求大于零
    log_content: str = None  # 字符串类型的字段，默认为None
    log_file_id: int = None  # 整数类型的字段，默认为None
    oper_dt: datetime = None  # 日期时间类型的字段，默认为None
    has_delete: int = 0


class pageRequest(BaseModel):
    id: int = Field(..., gt=0)
    pn: int = Field(..., gt=0)
    pg: int = Field(..., gt=0)
