import datetime
import hashlib
import json
import time
import uuid

from fastapi import APIRouter
from fastapi import Request, Header, HTTPException, Depends
import random

from model.db import session_db
from service.user import UserModel, SessionModel, UserinfoModel, SchoolModel, CollegeModel, MajorModel, ClassModel, \
    OperationModel,encrypted_password
from type.Celery import send_email
from type.page import page
from type.user import user_info_interface, \
    session_interface, email_interface, school_interface, class_interface, college_interface, major_interface, \
    password_interface, operation_interface, user_add_interface, admin_user_add_interface, login_interface
from utils.auth_login import auth_login, auth_register, auth_not_login, auth_school_exist, auth_college_exist, \
    auth_school_not_exist, auth_college_not_exist, auth_major_exist, auth_major_not_exist, auth_class_exist, \
    auth_class_not_exist
from utils.response import user_standard_response, page_response, status_response

users_router = APIRouter()
user_model = UserModel()
session_model = SessionModel()
user_info_model = UserinfoModel()
school_model = SchoolModel()
college_model = CollegeModel()
major_model = MajorModel()
class_model = ClassModel()
operation_model = OperationModel()



def get_email_token():  # 生成email的验证码
    email_token = ''
    for i in range(8):
        email_token += str(random.randint(0, 9))  # 生成八位随机验证码
    return email_token


def add_operation(service_type, service_id, func, parameters, oper_user_id):
    operation = operation_interface(service_type=service_type, service_id=service_id, func=func,
                                    parameters=parameters,
                                    oper_user_id=oper_user_id)
    operation_model.add_operation(operation)


@users_router.post("/register")  # 用户自己注册
@user_standard_response
async def user_register(request: Request, user=Depends(auth_register), user_agent: str = Header(None)):
    id = user_model.register_user(user)  # 添加一个user
    await user_send_email_code(user.email, request, 1, user_agent, 0)  # 发送邮件
    return {'message': '注册成功,请前往进行邮箱验证', 'status': 1, 'data': {'user_id': id}}


@users_router.post("/user_add")  # 管理员添加一个用户(未添加权限认证)
@user_standard_response
async def user_add(user_information: admin_user_add_interface, session=Depends(auth_login)):
    user = user_add_interface(username=user_information.username, password=user_information.password,
                              email=user_information.email, card_id=user_information.card_id)
    user_id = user_model.add_user(user)
    user_info = user_info_interface(user_id=user_id, realname=user_information.realname, gender=user_information.gender,
                                    major_id=user_information.major_id, class_id=user_information.class_id,
                                    enrollment_dt=user_information.enrollment_dt,
                                    graduation_dt=user_information.graduation_dt)
    user_info_model.add_userinfo(user_info)
    add_operation(0, user_id, '添加用户', '管理员添加一个用户', session['user_id'])
    return {'message': '添加成功', 'data': {'user_id': user_id}}


# 发送邮箱验证码
@user_standard_response
async def user_send_email_code(email: str, request: Request, token1=Depends(auth_not_login),
                               user_agent: str = Header(None), update: int = 0):
    token = str(uuid.uuid4().hex)  # 生成token
    email_token = get_email_token()  # 生成八位email_token
    id = 0
    if update == 0:  # 用户注册时发邮件
        id = user_model.get_user_by_email(email).id  # 查询出刚存进user表里数据的id
        add_operation(0, id, '用户注册', '用户注册并向其发送邮件', id)
    elif update == 1:  # 更改邮箱时发邮件
        id = token1['user_id']
        old_email = user_model.get_user_by_user_id(int(id))  # 新更改邮箱不能与原邮箱相同
        if old_email.email == email:
            raise HTTPException(
                status_code=409,
                detail="不能与原邮箱相同！",
            )
        add_operation(0, id, '修改绑定邮箱', '用户修改绑定邮箱并向新邮箱发送邮件', id)
    elif update == 2:  # 找回密码时发邮件
        id = token1
        add_operation(0, id, '找回密码', '找回密码时向绑定邮箱发送邮件', id)
    session = session_interface(user_id=int(id), ip=request.client.host,
                                func_type=1,
                                token=token, user_agent=user_agent, token_s6=email_token,
                                use_limit=1, exp_dt=(
                datetime.datetime.now() + datetime.timedelta(minutes=5)))  # 新建一个session
    id = session_model.add_session(session)
    send_email.delay(email, email_token)  # 异步发送邮件
    session.exp_dt = time.strptime(session.exp_dt.strftime(
        "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
    user_session = json.dumps(session.model_dump())
    session_db.set(token, user_session, ex=300)  # 缓存有效session(时效5分钟)
    return {'data': {'session_id': id}, 'message': '验证码已发送，请前往验证！', 'token_header': token}


@users_router.post("/register/verify_email_code")  # 验证用户输入的验证码是否正确
@user_standard_response
async def user_verify_email_code(token_s6: email_interface, token=Depends(auth_not_login),
                                 update: int = 0):
    if token_s6 is None:  # 没输入验证码
        raise HTTPException(
            status_code=409,
            detail="请输入验证码",
            headers={'status': '1'}
        )
    else:
        session = session_db.get(token)  # 从缓存中得到有效session
        user_session = session_model.get_session_by_token(token)  # 根据token获取用户的session
        if user_session is None:
            raise HTTPException(
                status_code=409,
                detail="验证码已过期",
            )
        if session is not None:  # 在缓存中能找到，说明该session有效
            session = json.loads(session)
            if session['token_s6'] == token_s6.token_s6:  # 输入的验证码正确
                session_model.update_session_use(user_session.id, 1)  # 把这个session使用次数设为1
                session_model.delete_session(user_session.id)  # 把这个session设为无效
                operation = operation_interface(service_type=0, service_id=user_session.user_id, func='注册成功',
                                                parameters='用户注册时输入了正确的邮箱验证码通过验证',
                                                oper_user_id=user_session.user_id)
                operation_model.add_operation(operation)
                if update == 0:
                    user_model.update_user_status(user_session.user_id, 0)
                    add_operation(0, user_session.user_id, '注册成功', '用户注册时输入了正确的邮箱验证码通过验证', user_session.user_id)
                    return {'message': '验证成功', 'status': 0, 'data': {'session_id': user_session.id}}
                elif update == 1:
                    user_model.update_user_email(user_session.user_id, token_s6.email)
                    add_operation(0, user_session.user_id, '修改邮箱成功', '修改邮箱时输入了正确的邮箱验证码通过验证', user_session.user_id)
                    return {'message': '验证成功', 'data': {'session_id': user_session.id}}
                elif update == 2:
                    add_operation(0, user_session.user_id, '找回密码成功', '找回密码时输入了正确的邮箱验证码通过验证', user_session.user_id)
                    return {'message': '验证成功', 'data': {'session_id': user_session.id}}
            else:
                raise HTTPException(
                    status_code=400,
                    detail="验证码有误"
                )
        else:  # 缓存中找不到，说明已无效
            session_model.delete_session(user_session.id)
            raise HTTPException(
                status_code=408,
                detail="验证码已过期，请重新发送"
            )


@users_router.get("/login")  # 登录
@user_standard_response
async def user_login(username: str, password: str, request: Request, user_agent: str = Header(None),
                     token=Depends(auth_not_login)):
    user_information = user_model.get_user_by_username(username)  # 先查看要登录的用户名是否存在
    if user_information is None:  # 用户名不存在
        raise HTTPException(
            status_code=404,
            detail="用户名或密码不正确，请重新输入",
            headers={'status': '1'}
        )
    else:  # 用户名存在
        new_password = encrypted_password(password,user_information.registration_dt)  # 判定输入的密码是否正确
        if new_password == user_information.password:
            token = str(uuid.uuid4().hex)
            session = session_interface(user_id=int(user_information.id), ip=request.client.host,
                                        func_type=0,
                                        token=token, user_agent=user_agent, exp_dt=(
                        datetime.datetime.now() + datetime.timedelta(days=14)))
            id = session_model.add_session(session)
            session.exp_dt = time.strptime(session.exp_dt.strftime(
                "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
            user_session = json.dumps(session.model_dump())
            session_db.set(token, user_session, ex=1209600)  # 缓存有效session
            add_operation(0, int(user_information.id), '用户登录', '用户通过输入用户名和密码成功登录', int(user_information.id))
            return {'message': '登陆成功', 'token': token, 'status': 0, 'data': {'session_id': id}}
        else:
            raise HTTPException(
                status_code=401,
                detail="用户名或密码不正确，请重新输入",
                headers={'status': '1'}
            )


@users_router.put("/logout")  # 下线
@user_standard_response
async def user_logout(session=Depends(auth_login)):
    token = session['token']
    mes = session_model.delete_session_by_token(token)  # 将session标记为已失效
    session_db.delete(token)  # 在缓存中删除
    add_operation(0, session['user_id'], '用户退出登录', '用户退出了登录', session['user_id'])
    return {'message': '下线成功', 'data': {'result': mes}, 'token': '-1'}


@users_router.post("/user_bind_information")  # 自己注册的用户绑定个人信息
@user_standard_response
async def user_bind_information(user_data: user_info_interface, request: Request, session=Depends(auth_login)):
    user_model.update_user_card_id(session['user_id'], user_data.card_id)  # 更新用户的card_id
    user_data.user_id = session['user_id']
    id = user_info_model.add_userinfo(user_data)  # 在user_info表里添加
    add_operation(0, session['user_id'], '用户绑定个人信息', '用户通过输入学号，真实姓名，性别，专业，班级，入学时间与毕业时间进行绑定',
                  session['user_id'])  # 添加一个绑定个人信息的操作
    return {'message': '绑定成功', 'data': {'user_id': id}}


@users_router.put("/email_update")  # 修改绑定邮箱
@user_standard_response
async def user_email_update(email: email_interface, request: Request, session=Depends(auth_login),
                            user_agent: str = Header(None)):
    result = await user_send_email_code(email.email, request, session, user_agent, 1)  # 向新邮箱发送验证码
    ans = json.loads(result.body)
    token_header = result.headers  # 将新生成的session的token加入到header里
    return {'data': {'session_id': ans['data']['session_id']}, 'message': ans['message'],
            'token_header': token_header['token']}


@users_router.put("/username_update")  # 修改用户名
@user_standard_response
async def username_update(username: login_interface, session=Depends(auth_login)):
    user_id = session['user_id']
    exist_username = user_model.get_user_by_username(username.username)
    if exist_username is not None:
        raise HTTPException(
            status_code=401,
            detail="用户名重复，请重新输入"
        )
    user_model.update_user_username(user_id, username.username)  # 更新username
    add_operation(0, user_id, '用户修改用户名', '用户通过输入新用户名进行修改',
                  user_id)  # 添加一个修改用户名的操作
    return {'message': '修改成功', 'data': {'user_id': user_id}}


@users_router.post("/email_update/verify_update_email")  # 验证用户输入的验证码是否正确
@user_standard_response
async def user_verify_update_email(token_s6: email_interface, token: str = Header(None), session=Depends(auth_login)):
    result = await user_verify_email_code(token_s6, token, 1)  # 验证验证码是否输入正确
    ans = json.loads(result.body)
    return {'data': {'session_id': ans['data']['session_id']}, 'message': ans['message']}


@users_router.put("/password_update")  # 更改密码
@user_standard_response
async def user_password_update(password: password_interface, session=Depends(auth_login)):
    user_id = session['user_id']
    user = user_model.get_user_by_user_id(user_id)
    if user.password != encrypted_password(password.old_password, user.registration_dt):  # 原密码输入错误
        raise HTTPException(
            status_code=401,
            detail="密码输入不正确"
        )
    new_password = encrypted_password(password.new_password, user.registration_dt)
    if user.password == new_password:  # 新密码与旧密码相同
        raise HTTPException(
            status_code=401,
            detail="新密码不能与旧密码相同"
        )
    id = user_model.update_user_password(user_id, new_password)  # 更新新密码
    add_operation(0, id, '用户更改密码', '用户通过输入原密码，新密码进行更改密码', id)  # 更改密码
    return {'data': {'user_id': id}, 'message': '修改成功'}


@users_router.post("/get_back_password")  # 找回密码
@user_standard_response
async def user_password_get_back(email: email_interface, request: Request, user_agent: str = Header(None)):
    user_information = user_model.get_user_by_username(email.username)
    if user_information is None:  # 看看有没有这个用户名
        raise HTTPException(
            status_code=401,
            detail="没有该用户"
        )
    if email.card_id != email.card_id:  # 看看有没有这个学号
        raise HTTPException(
            status_code=401,
            detail="没有该学号"
        )
    if user_information.email != email.email:  # 看看有没有这个邮箱
        raise HTTPException(
            status_code=401,
            detail="邮箱不正确，不是之前绑定的邮箱"
        )
    result = await user_send_email_code(email.email, request, user_information.id, user_agent, 2)

    ans = json.loads(result.body)
    token_header = result.headers
    return {'data': {'session_id': ans['data']['session_id']}, 'message': ans['message'],
            'token_header': token_header['token']}


@users_router.post("/get_back_password/verify_email_code")  # 验证找回密码时用户输入的验证码是否正确
@user_standard_response
async def user_verify_update_email(token_s6: email_interface, token: str = Header(None)):
    result = await user_verify_email_code(token_s6, token, 2)
    ans = json.loads(result.body)
    return {'data': {'session_id': ans['data']['session_id']}, 'message': ans['message']}


@users_router.put("/get_back_password/set_password")  # 找回密码后用户设置密码
@user_standard_response
async def user_set_password(password: email_interface, token: str = Header(None)):
    user_information = session_model.get_session_by_token_force(token)  # 查出user_id
    user_model.update_user_password(user_information.user_id, encrypted_password(password.password,user_information.registration_dt))  # 设置密码
    add_operation(0, user_information.user_id, '用户重设密码', '用户通过输入新密码进行更改密码', user_information.user_id)  # 重设密码
    return {'data': {'user_id': user_information.user_id}, 'message': '修改成功'}


@users_router.get("/status")  # 检查用户登录状态
@status_response
async def user_get_status(token: str = Header(None)):
    login_status = 1
    session = session_db.get(token)
    if session is not None:  # 有效session中有，说明登录了
        login_status = 0
        user_id = json.loads(session)['user_id']  # 从缓存中获取user_id
    else:
        user_id = session_model.get_session_by_token(token).user_id  # 根据session获取user_id
    user_information = user_model.get_user_by_user_id(user_id)  # 查找出用户的信息
    account_status = user_information.status  # 帐号状态
    data = dict()
    realname = user_info_model.get_userinfo_by_user_id(user_id).realname
    data['username'] = user_information.username  # 返回用户的基本信息
    data['realname'] = realname
    data['email'] = user_information.email
    data['card_id'] = user_information.card_id
    return {'message': '结果如下', 'data': data, 'login_status': login_status, 'account_status': account_status}


@users_router.get("/error")  # 检查用户异常状态原因
@user_standard_response
async def user_register(token: str = Header(None)):
    user_id = session_model.get_session_by_token(token).user_id
    reason = operation_model.get_operation_by_service_func(0, user_id, '用户封禁')  # 查看被封禁原因
    username = user_model.get_user_by_user_id(reason.oper_user_id).username  # 看被谁封禁
    return {'message': '用户异常状态原因', 'data': {'封禁原因': reason.parameters, '封禁人': username}}


@users_router.post("/school_add")  # 管理员添加学校(未添加权限认证)
@user_standard_response
async def user_school_add(session=Depends(auth_login), school_data=Depends(auth_school_exist)):
    # 判断是否有权限
    # 如果有权限
    id = school_model.add_school(school_data)
    add_operation(1, id, '添加学校', '管理员通过输入学校名称和学校简称添加一个学校', session['user_id'])  # 添加一个学校
    return {'message': '建立成功', 'data': {'school_id': id}}


@users_router.get("/school_view")  # 查看管理员所能操作的所有学校(未添加权限认证)
@page_response
async def user_school_view(pageNow: int, pageSize: int):
    # 判断是否有权限
    # 如果有权限
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_school = school_model.get_school_by_admin(Page)  # 以分页形式返回
    if all_school == []:
        raise HTTPException(
            status_code=404,
            detail="没有可操作学校"
        )
    school_data = []
    for school in all_school:
        temp = school_interface()
        temp_dict = temp.model_validate(school).model_dump()
        id = school_model.get_school_by_name(temp_dict['name']).id
        temp_dict['id'] = id
        school_data.append(temp_dict)
    return {'message': '学校如下', 'pageIndex': pageNow, "pageSize": pageSize, "totalNum": len(all_school),
            "rows": school_data}


@users_router.delete("/school_delete/{school_id}")  # 管理员删除学校(未添加权限认证)
@user_standard_response
async def user_school_delete(session=Depends(auth_login), school_id=Depends(auth_school_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = school_model.delete_school(school_id)  # 在school表中将这个学校has_delete设为1
    add_operation(1, id, '删除学校', '管理员通过选择学校来删除一个学校', session['user_id'])  # 删除一个学校
    return {'message': '删除成功', 'data': {'school_id': id}}


@users_router.put("/school_update/{school_id}")  # 管理员修改学校信息(未添加权限认证)
@user_standard_response
async def user_school_update(session=Depends(auth_login), school_id=Depends(auth_school_not_exist),
                             school_data=Depends(auth_school_exist)):
    # 判断是否有权限
    # 如果有权限
    if school_data.name is not None:
        school_model.update_school_name(school_id, school_data.name)
        add_operation(1, school_id, '修改学校名字', '管理员通过选择学校来修改学校名字', session['user_id'])  # 修改学校名字
    if school_data.school_abbreviation is not None:
        school_model.update_school_abbreviation(school_id, school_data.school_abbreviation)
        add_operation(1, school_id, '修改学校昵称', '管理员通过选择学校来修改学校昵称', session['user_id'])  # 修改学校昵称
    return {'message': '修改成功', 'data': {'school_id': school_id}}


@users_router.post("/college_add")  # 管理员添加学院(未添加权限认证)
@user_standard_response
async def user_college_add(session=Depends(user_login), college_data=Depends(auth_college_exist)):
    # 判断是否有权限
    # 如果有权限
    id = college_model.add_college(college_data)
    add_operation(2, id, '添加学院', '管理员通过选择学校和输入学院名称添加一个学院', session['user_id'])  # 添加一个学院
    return {'message': '建立成功', 'data': {'college_id': id}}


@users_router.delete("/college_delete/{college_id}")  # 管理员删除学院(未添加权限认证)
@user_standard_response
async def user_college_delete(session=Depends(user_login), college_id=Depends(auth_college_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = college_model.delete_college(college_id)
    add_operation(2, id, '删除学院', '管理员通过选择学院删除一个学院', session['user_id'])  # 删除一个学院
    return {'message': '删除成功', 'data': {'college_id': id}}


@users_router.get("/college_view")  # 查看管理员所能操作的所有学院(未添加权限认证)
@page_response
async def user_college_view(pageNow: int, pageSize: int):
    # 判断是否有权限
    # 如果有权限
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_college = college_model.get_college_by_admin(Page)  # 以分页形式返回
    if all_college == []:
        raise HTTPException(
            status_code=404,
            detail="没有可操作专业"
        )
    college_data = []
    for college in all_college:
        temp = college_interface()
        temp_dict = temp.model_validate(college).model_dump()
        ttt = college_interface(name=temp_dict['name'], school_id=temp_dict['school_id'])
        id = college_model.get_college_by_name(ttt).id
        temp_dict['id'] = id
        school_name = school_model.get_school_by_id(temp_dict['school_id']).name
        temp_dict['school_name'] = school_name
        college_data.append(temp_dict)
    return {'message': '学院如下', 'pageIndex': pageNow, "pageSize": pageSize, "totalNum": len(all_college),
            "rows": college_data}


@users_router.put("/college_update/{college_id}")  # 管理员修改学院信息(未添加权限认证)
@user_standard_response
async def user_college_update(session=Depends(user_login), college_id=Depends(auth_college_not_exist),
                              college_data=Depends(auth_college_exist)):
    # 判断是否有权限
    # 如果有权限
    college_model.update_college_school_id_name(college_id, college_data.school_id, college_data.name)
    add_operation(2, college_id, '修改学院信息', '管理员通过选择学院修改学院信息', session['user_id'])  # 删除一个学院
    return {'message': '修改成功', 'data': {'college_id': college_id}}


@users_router.post("/major_add")  # 管理员添加专业(未添加权限认证)
@user_standard_response
async def user_major_add(session=Depends(user_login), major_data=Depends(auth_major_exist)):
    # 判断是否有权限
    # 如果有权限
    id = major_model.add_major(major_data)
    add_operation(3, id, '添加专业', '管理员通过选择学校和学院并输入专业名称添加一个专业', session['user_id'])  # 添加一个专业
    return {'message': '建立成功', 'data': {'major_id': id}}


@users_router.delete("/major_delete/{major_id}")  # 管理员删除专业(未添加权限认证)
@user_standard_response
async def user_major_delete(session=Depends(user_login), major_id=Depends(auth_major_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = major_model.delete_major(major_id)
    add_operation(3, id, '删除专业', '管理员通过选择专业删除一个专业', session['user_id'])  # 删除一个专业
    return {'message': '删除成功', 'data': {'major_id': id}}


@users_router.put("/major_update/{major_id}")  # 管理员修改专业信息(未添加权限认证)
@user_standard_response
async def user_major_update(session=Depends(user_login), major_id=Depends(auth_major_not_exist),
                            major_data=Depends(auth_major_exist)):
    # 判断是否有权限
    # 如果有权限
    id = major_model.update_major_college_id_name(major_id, major_data.college_id, major_data.name)
    add_operation(3, id, '修改专业信息', '管理员通过选择专业修改一个专业的信息', session['user_id'])  # 删除一个专业
    return {'message': '修改成功', 'data': {'major_id': id}}


@users_router.get("/major_view")  # 查看管理员所能操作的所有专业(未添加权限认证)
@page_response
async def user_major_view(pageNow: int, pageSize: int):
    # 判断是否有权限
    # 如果有权限
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_major = major_model.get_major_by_admin(Page)  # 以分页形式返回
    if all_major == []:
        raise HTTPException(
            status_code=404,
            detail="没有可操作专业"
        )
    major_data = []
    for major in all_major:  # 遍历查询结果
        temp = major_interface()
        temp_dict = temp.model_validate(major).model_dump()  # 查询出来的结果转字典
        school_id = college_model.get_college_by_id(temp_dict['college_id']).school_id  # 查出school_id
        temp_dict['school_id'] = school_id
        ttt = major_interface(name=temp_dict['name'], school_id=school_id,
                              college_id=temp_dict['college_id'])  # 初始化一个major_interface
        id = major_model.get_major_by_name(ttt).id  # 查找出当major的id
        temp_dict['id'] = id  # 加入到结果里
        school_name = school_model.get_school_by_id(school_id).name  # 根据school_id查出school_name
        temp_dict['school_name'] = school_name  # 加入到结果里
        college_name = college_model.get_college_by_id(temp_dict['college_id']).name  # 根据college_id查出college_name
        temp_dict['college_name'] = college_name  # 加入到结果里
        major_data.append(temp_dict)
    return {'message': '学院如下', 'pageIndex': pageNow, "pageSize": pageSize, "totalNum": len(all_major),
            "rows": major_data}


@users_router.post("/class_add")  # 管理员添加班级(未添加权限认证)
@user_standard_response
async def user_class_add(session=Depends(user_login), class_data=Depends(auth_class_exist)):
    # 判断是否有权限
    # 如果有权限
    id = class_model.add_class(class_data)
    add_operation(4, id, '添加班级', '管理员通过选择学校和学院并输入班级名称添加一个班级', session['user_id'])  # 添加一个班级
    return {'message': '建立成功', 'data': {'class_id': id}}


@users_router.delete("/class_delete/{class_id}")  # 管理员删除班级(未添加权限认证)
@user_standard_response
async def user_class_delete(session=Depends(user_login), class_id=Depends(auth_class_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = class_model.delete_class(class_id)
    add_operation(4, id, '删除班级', '管理员通过选择班级删除一个班级', session['user_id'])  # 删除一个班级
    return {'message': '删除成功', 'data': {'class_id': id}}


@users_router.put("/class_update/{class_id}")  # 管理员修改班级信息(未添加权限认证)
@user_standard_response
async def user_class_update(session=Depends(user_login), class_id=Depends(auth_class_not_exist),
                            class_data=Depends(auth_class_exist)):
    # 判断是否有权限
    # 如果有权限
    id = class_model.update_major_college_id_name(class_id, class_data.college_id, class_data.name)
    add_operation(4, id, '修改班级信息', '管理员通过选择班级修改一个班级的信息', session['user_id'])  # 修改班级信息
    return {'message': '修改成功', 'data': {'class_id': id}}


@users_router.get("/class_view")  # 查看管理员所能操作的所有班级(未添加权限认证)
@page_response
async def user_class_view(pageNow: int, pageSize: int):
    # 判断是否有权限
    # 如果有权限
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_class = class_model.get_class_by_admin(Page)  # 以分页形式返回
    if all_class == []:
        raise HTTPException(
            status_code=404,
            detail="没有可操作班级"
        )
    class_data = []
    for clas in all_class:  # 遍历查询结果
        temp = class_interface()
        temp_dict = temp.model_validate(clas).model_dump()  # 查询出来的结果转字典
        school_id = college_model.get_college_by_id(temp_dict['college_id']).school_id  # 查出school_id
        temp_dict['school_id'] = school_id
        ttt = class_interface(name=temp_dict['name'], school_id=school_id,
                              college_id=temp_dict['college_id'])  # 初始化一个class_interface
        id = class_model.get_class_by_name(ttt).id  # 查找出当class的id
        temp_dict['id'] = id  # 加入到结果里
        school_name = school_model.get_school_by_id(school_id).name  # 根据school_id查出school_name
        temp_dict['school_name'] = school_name  # 加入到结果里
        college_name = college_model.get_college_by_id(temp_dict['college_id']).name  # 根据college_id查出college_name
        temp_dict['college_name'] = college_name  # 加入到结果里
        class_data.append(temp_dict)
    return {'message': '班级如下', 'pageIndex': pageNow, "pageSize": pageSize, "totalNum": len(all_class),
            "rows": class_data}
