from typing import List, Optional

from fastapi import Depends
from pydantic import BaseModel


class role_base(BaseModel):  # 创建角色信息
    user_id: int
    role_name: str
    role_superiorId: int


def ser_role_add(data: role_base):
    return data


class attribute_role_base(BaseModel):  # 分配用户角色信息
    user_id: int
    role_name: str

class attribute_privilege_base(BaseModel):  # 为角色添加权限信息
    user_id: int
    privilege_name: str


class RolePydantic(BaseModel):  # 将数据库查询结果转化为字典的模型（对应Role表）
    id: int
    name: str
    description: str
    superiorId: int
    template: int
    template_val: Optional[str] = None
    tplt_id: Optional[int] = None
    status: int
    superiorListId: str
    has_delete: int

    class Config:
        orm_mode = True
