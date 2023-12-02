import json
from fastapi import Request, HTTPException, Depends
from model.db import session_db
from service.user import SessionModel, UserinfoModel

session_model = SessionModel()
user_info_model = UserinfoModel()


def auth_login(request: Request):  # 用来判断用户是否登录
    token = request.cookies.get("SESSION")
    if token is not None:
        session = session_db.get(token)  # 有效session中没有
        if session is None:
            session_model.delete_session_by_token(token)
            raise HTTPException(
                status_code=401,
                detail="用户未登录",
            )
        return json.loads(session)  # 登陆了就返回用户登录的session
    else:
        raise HTTPException(
            status_code=401,
            detail="用户未登录"
        )


def auth_not_login(request: Request):  # 用来判断用户是否没登录
    token = request.cookies.get("SESSION")
    if token is None:
        return token
    user = session_db.get(token)  # 有效session中有
    if user is not None and json.loads(user)['func_type'] == 0:
        raise HTTPException(
            status_code=401,
            detail="用户已登录"
        )
    return token


def oj_login(session=Depends(auth_login)):  # 用来判断用户oj是否绑定
    username = user_info_model.get_oj_exist_by_user_id(session['user_id'])
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="请先绑定oj账号"
        )
    # 用账号密码登录获取token
    token = 1
    res = {"token": token, "user_id": session['user_id']}
    return res


def oj_not_login(session=Depends(auth_login)):  # 用来判断用户oj是否绑定
    username = user_info_model.get_oj_exist_by_user_id(session['user_id'])
    if username is not None:
        raise HTTPException(
            status_code=401,
            detail="您已绑定oj账号"
        )
    return session