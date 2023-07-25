from fastapi import Depends, Security, HTTPException
from fastapi import Request

from utils.auth_login import auth_login


def auth_permission(request: Request):
    user = auth_login(request)

    permission_key = request.url.path.replace('/', '_')

    permission = None

    if not permission:
        raise HTTPException(
            status_code=403,
            detail="No permission",
        )

    return user
