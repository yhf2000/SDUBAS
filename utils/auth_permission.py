from fastapi import Depends, Security, HTTPException
from fastapi import Request

from utils.auth_login import auth_login
from model.permissions import User, UserRole, RolePrivilege, Role
from model.db import dbSession
from service.permissions import roleModel


def auth_permission(request: Request):
    user_id = int(request.headers.get("user_id"))
    # user = auth_login(request)
    permission_key = request.url.path.replace('/', '_')
    permission = None

    db = roleModel()
    role_list = db.search_role_by_user(user_id)
    privilege_set = db.search_privilege_by_role(role_list)

    """
    if not permission:
        raise HTTPException(
            status_code=403,
            detail="No permission",
        )
    """
    return user_id
