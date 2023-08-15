from fastapi import APIRouter, Depends, FastAPI, Request

import type.permissions
from service.permissions import roleModel
from utils.response import standard_response
from utils.auth_permission1 import permission

permissions_router = APIRouter()


@permissions_router.post("/add")  # 创建角色
async def add(data: type.permissions.role_base):
    db = roleModel()
    return {"new_role": db.get_role_info_by_id(db.create(data))}


@permissions_router.post("/delete")  # 删除角色
@standard_response
async def delete(data: str):
    db = roleModel()
    return {"status": db.delete(data)}


@permissions_router.post("/attribute_role")  # 分配用户角色
async def attribute_role(data: type.permissions.attribute_role_base):
    db = roleModel()
    return {"attribute_role": db.get_user_role_info_by_id(db.attribute_user_role(data))}


@permissions_router.post("/attribute_privilege")  # 为角色添加权限
@standard_response
async def attribute_privilege(data: type.permissions.attribute_privilege_base):
    db = roleModel()
    return {"status": db.attribute_privilege(data)}


@permissions_router.post("/login")
async def login(request: Request):
    token = request.headers.get("SESSION")

    return {"message": f"欢迎回来，{token}！"}


@permissions_router.post("/test_permission")
async def login(request: Request):
    token = request.headers.get("SESSION")

    permi = permission()
    result = permi.auth_permission(request)

    return {"message": result}
