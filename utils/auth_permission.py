from fastapi import HTTPException
from fastapi import Request

from service.permissions import roleModel
from utils.auth_login import auth_login


def auth_permission(request: Request):
    db = roleModel()
    user = auth_login(request)
    permission_key = request.url.path
    permission = None
    role_list = db.search_role_by_user(user['user_id'])
    privilege_set = db.search_privilege_by_role(role_list)
    permission = db.check_permission(permission_key, privilege_set)
    if not permission:
        raise HTTPException(
            status_code=403,
            detail="No permission",
        )
    return user['user_id']
