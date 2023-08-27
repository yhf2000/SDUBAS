from fastapi import Depends, Security, HTTPException
from fastapi import Request
from model.user import User
from model.permissions import  UserRole, RolePrivilege, Role
from model.db import dbSession
from service.permissions import roleModel


def auth_permission(request: Request):

    db = roleModel()
    user_id = int(request.headers.get("user_id"))
    # user = auth_login(request)
    permission_key = request.url.path
    permission = None
    role_list = db.search_role_by_user(user_id)
    privilege_set = db.search_privilege_by_role(role_list)
    permission = db.check_permission(permission_key, privilege_set)
    if not permission:
        raise HTTPException(
            status_code=403,
            detail="No permission",
        )
    return user_id
