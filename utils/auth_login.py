from fastapi import Request, HTTPException


def auth_login(request: Request):
    token = request.cookies.get("SESSION")

    crud = None
    db = None

    user = crud.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
