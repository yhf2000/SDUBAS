from typing import List, Optional

from fastapi import Depends
from pydantic import BaseModel


class create_user_role_base(BaseModel):
    role_id: int
    user_id: int


class create_role_base(BaseModel):  # 创建角色信息
    role_name: str
    role_superiorId: int


class delete_role_base(BaseModel):  # 删除角色信息
    role_name: str


class attribute_role_base(BaseModel):  # 分配用户角色信息
    user_id: int
    role_name: str


class attribute_privilege_base(BaseModel):  # 为角色添加权限信息
    user_id: int
    role_name: str
    privilege_name: str
    privilege_id: int


class attribute_role_for_work_base(BaseModel):  # 为业务分配角色
    service_type: int
    service_id: int
    role_name: str
    role_id: int


class Add_Role_For_Work_Base(BaseModel):
    service_type: int = None
    service_id: int = None
    role_name: str
    role_id: int = None
    status: Optional[int] = None
    has_delete: int = 0


class Return_Service_Id(BaseModel):  # 返回业务id
    service_type: int
    name: str


class Return_User_Id(BaseModel):  # 返回用户id
    service_type: int
    service_id: int


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
        from_attributes = True
