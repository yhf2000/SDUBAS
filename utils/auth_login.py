import ast
import json
import time

import requests
from fastapi import Request, HTTPException, Depends
from model.db import session_db, oj_db
from service.file import RSAModel
from service.user import SessionModel, UserinfoModel
from type.functions import decrypt_aes_key_with_rsa

session_model = SessionModel()
user_info_model = UserinfoModel()
RSA_model = RSAModel()

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
    information = user_info_model.get_oj_exist_by_user_id(session['user_id'])
    if information is None:
        raise HTTPException(
            status_code=401,
            detail="请先绑定oj账号"
        )
    oj_user = oj_db.get(session['user_id'])  # 有效session中有
    if oj_user is not None:
        data = ast.literal_eval(oj_user.decode('utf-8'))
    else:
        private_key = RSA_model.get_private_key_by_user_id(1)[0]
        while 1:
            user_info = {
                "username": information[0],
                "password": decrypt_aes_key_with_rsa(information[1], private_key).decode('utf-8')
            }
            # user_info = {
            #     "username": 'sdubas_bind',
            #     "password": 'LuX2y2Kkg!YfV:N'
            # }
            response = requests.post(f"https://43.143.149.67:7359/api/user/login", json=user_info, verify=False)
            if response.status_code == 200:
                data = response.headers
                oj_db.set(session['user_id'],str(data),ex=1400000)
                break
            else:
                time.sleep(2)
    token = data['Set-Cookie'].split(';')[0]
    headers = {
        "Cookie": token
    }
    return headers


def oj_not_login(session=Depends(auth_login)):  # 用来判断用户oj是否绑定
    username = user_info_model.get_oj_exist_by_user_id(session['user_id'])
    if username[0] is not None:
        raise HTTPException(
            status_code=401,
            detail="您已绑定oj账号"
        )
    return session