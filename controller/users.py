import datetime
import json
import time
import uuid

from fastapi import APIRouter
from fastapi import Request, Header, HTTPException, Depends

from model.db import session_db
from service.user import UserModel, SessionModel, UserinfoModel, SchoolModel, CollegeModel, MajorModel, ClassModel
from type.celery import send_email
from type.page import page
from type.user import user_info_interface, MD5, get_email_token, \
    session_interface, nothing, school_interface, class_interface, college_interface, major_interface
from utils.auth_login import auth_login, auth_register, auth_not_login, auth_school_exist, auth_college_exist, \
    auth_school_not_exist, auth_college_not_exist, auth_major_exist, auth_major_not_exist, auth_class_exist, \
    auth_class_not_exist
from utils.response import user_standard_response, page_response

users_router = APIRouter()
user_model = UserModel()
session_model = SessionModel()
user_info_model = UserinfoModel()
school_model = SchoolModel()
college_model = CollegeModel()
major_model = MajorModel()
class_model = ClassModel()

@users_router.post("/user/register")  # 用户自己注册
@user_standard_response
async def user_register(user=Depends(auth_register)):
    user.password = MD5(user.password)  # 使用MD5对密码进行加密
    id = user_model.add_user(user)  # 添加一个user
    return {'message': '注册成功,请前往进行邮箱验证', 'status': 1, 'data': {'user_id': id}}


@users_router.post("/user/send_email_code")  # 发送邮件验证码
@user_standard_response
async def user_send_email_code(email: nothing, request: Request, token1=Depends(auth_not_login),
                               user_agent: str = Header(None), update: int = 0):
    token = str(uuid.uuid4().hex)
    email_token = get_email_token()
    id = 0
    if update == 0:
        id = user_model.get_user_by_email(email.email).id  # 查询出刚存进user表里数据的id
    else:
        id = token1['user_id']
        old_email = user_model.get_user_by_user_id(int(id))
        if old_email.email == email.email:
            raise HTTPException(
                status_code=409,
                detail="不能与原邮箱相同！",
            )

    session = session_interface(user_id=int(id), ip=request.client.host,
                                func_type=1,
                                token=token, user_agent=user_agent, token_s6=email_token,
                                use_limit=1, exp_dt=(
                datetime.datetime.now() + datetime.timedelta(minutes=5)))  # 新建一个session
    id = session_model.add_session(session)
    send_email.delay(email.email, email_token)  # 异步发送邮件
    session.exp_dt = time.strptime(session.exp_dt.strftime(
        "%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")  # 将datetime转化为字符串以便转为json
    user_session = json.dumps(session.model_dump())
    session_db.set(token, user_session, ex=300)  # 缓存有效session(时效5分钟)
    return {'data': {'session_id': id}, 'message': '验证码已发送，请前往验证！', 'token_header': token, 'email_header': email.email}


@users_router.post("/user/verify_email_code")  # 验证用户输入的验证码是否正确
@user_standard_response
async def user_verify_email_code(token_s6: nothing, email: str, token=Depends(auth_not_login), update: int = 0):
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
                session_model.update_session_use(user_session.id, 1)
                session_model.delete_session(user_session.id)
                if update == 0:
                    user_model.update_user_status(user_session.user_id, 0)
                    return {'message': '验证成功', 'status': 0, 'data': {'session_id': user_session.id}}
                else:
                    user_model.update_user_email(user_session.user_id, email)
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


@users_router.get("/user/login")  # 登录
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
        new_password = MD5(password)  # 判定输入的密码是否正确
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
            return {'message': '登陆成功', 'token': token, 'status': 0, 'data': {'session_id': id}}
        else:
            raise HTTPException(
                status_code=401,
                detail="用户名或密码不正确，请重新输入",
                headers={'status': '1'}
            )


@users_router.put("/user/logout")  # 下线
@user_standard_response
async def user_logout(session=Depends(auth_login)):
    token = session['token']
    mes = session_model.delete_session_by_token(token)
    session_db.delete(token)
    return {'message': '下线成功', 'data': {'result': mes}, 'token': '-1'}


@users_router.post("/user/user_bind_information")  # 自己注册的用户绑定个人信息
@user_standard_response
async def user_bind_information(user_data: user_info_interface, request: Request, session=Depends(auth_login)):
    user_model.update_user_card_id(session['user_id'], user_data.card_id)
    id = user_info_model.add_userinfo(user_data, session['user_id'])
    return {'message': '绑定成功', 'data': {'user_id': id}}


@users_router.put("/user/email_update")  # 修改绑定邮箱
@user_standard_response
async def user_email_update(email: nothing, request: Request, session=Depends(auth_login),
                            user_agent: str = Header(None)):
    result = await user_send_email_code(email, request, session, user_agent, 1)
    ans = json.loads(result.body)
    token_header = result.headers
    return {'data': {'session_id': ans['data']['session_id']}, 'message': ans['message'],
            'token_header': token_header['token']}


@users_router.post("/user/verify_update_email")  # 验证用户输入的验证码是否正确
@user_standard_response
async def user_verify_update_email(token_s6: nothing, email: str = Header(None), token=Depends(auth_not_login)):
    result = await user_verify_email_code(token_s6, email, token, 1)
    ans = json.loads(result.body)
    return {'data': {'session_id': ans['data']['session_id']}, 'message': ans['message']}


@users_router.post("/user/school_add")  # 管理员添加学校(未添加权限认证)
@user_standard_response
async def user_school_add(school_data=Depends(auth_school_exist), exist=Depends()):
    # 判断是否有权限
    # 如果有权限
    id = school_model.add_school(school_data)
    return {'message': '建立成功', 'data': {'school_id': id}}


@users_router.get("/user/school_view")  # 查看管理员所能操作的所有学校(未添加权限认证)
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


@users_router.delete("/user/school_delete/{school_id}")  # 管理员删除学校(未添加权限认证)
@user_standard_response
async def user_school_delete(school_id=Depends(auth_school_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = school_model.delete_school(school_id)  # 在school表中将这个学校has_delete设为1
    return {'message': '删除成功', 'data': {'school_id': id}}


@users_router.put("/user/school_update/{school_id}")  # 管理员修改学校信息(未添加权限认证)
@user_standard_response
async def user_school_update(school_id=Depends(auth_school_not_exist), school_data=Depends(auth_school_exist)):
    # 判断是否有权限
    # 如果有权限

    if school_data.name is not None:
        school_model.update_school_name(school_id, school_data.name)
    if school_data.school_abbreviation is not None:
        school_model.update_school_abbreviation(school_id, school_data.school_abbreviation)
    return {'message': '修改成功', 'data': {'school_id': school_id}}


@users_router.post("/user/college_add")  # 管理员添加学院(未添加权限认证)
@user_standard_response
async def user_college_add(college_data=Depends(auth_college_exist)):
    # 判断是否有权限
    # 如果有权限
    id = college_model.add_college(college_data)
    return {'message': '建立成功', 'data': {'college_id': id}}


@users_router.delete("/user/college_delete/{college_id}")  # 管理员删除学院(未添加权限认证)
@user_standard_response
async def user_college_delete(college_id=Depends(auth_college_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = college_model.delete_college(college_id)
    return {'message': '删除成功', 'data': {'college_id': id}}


@users_router.get("/user/college_view")  # 查看管理员所能操作的所有学院(未添加权限认证)
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


@users_router.put("/user/college_update/{college_id}")  # 管理员修改学院信息(未添加权限认证)
@user_standard_response
async def user_college_update(college_id=Depends(auth_college_not_exist), college_data=Depends(auth_college_exist)):
    # 判断是否有权限
    # 如果有权限
    college_model.update_college_school_id_name(college_id, college_data.school_id, college_data.name)
    return {'message': '修改成功', 'data': {'college_id': college_id}}


@users_router.post("/user/major_add")  # 管理员添加专业(未添加权限认证)
@user_standard_response
async def user_major_add(major_data=Depends(auth_major_exist)):
    # 判断是否有权限
    # 如果有权限
    id = major_model.add_major(major_data)
    return {'message': '建立成功', 'data': {'major_id': id}}


@users_router.delete("/user/major_delete/{major_id}")  # 管理员删除专业(未添加权限认证)
@user_standard_response
async def user_major_delete(major_id=Depends(auth_major_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = major_model.delete_major(major_id)
    return {'message': '删除成功', 'data': {'major_id': id}}


@users_router.put("/user/major_update/{major_id}")  # 管理员修改专业信息(未添加权限认证)
@user_standard_response
async def user_major_update(major_id=Depends(auth_major_not_exist), major_data=Depends(auth_major_exist)):
    # 判断是否有权限
    # 如果有权限
    id = major_model.update_major_college_id_name(major_id, major_data.college_id, major_data.name)
    return {'message': '修改成功', 'data': {'major_id': id}}


@users_router.get("/user/major_view")  # 查看管理员所能操作的所有专业(未添加权限认证)
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



@users_router.post("/user/class_add")  # 管理员添加班级(未添加权限认证)
@user_standard_response
async def user_class_add(class_data=Depends(auth_class_exist)):
    # 判断是否有权限
    # 如果有权限
    id = class_model.add_class(class_data)
    return {'message': '建立成功', 'data': {'class_id': id}}


@users_router.delete("/user/class_delete/{class_id}")  # 管理员删除班级(未添加权限认证)
@user_standard_response
async def user_class_delete(class_id=Depends(auth_class_not_exist)):
    # 判断是否有权限
    # 如果有权限
    id = class_model.delete_class(class_id)
    return {'message': '删除成功', 'data': {'class_id': id}}


@users_router.put("/user/class_update/{class_id}")  # 管理员修改班级信息(未添加权限认证)
@user_standard_response
async def user_class_update(class_id=Depends(auth_class_not_exist), class_data=Depends(auth_class_exist)):
    # 判断是否有权限
    # 如果有权限
    id = class_model.update_major_college_id_name(class_id, class_data.college_id, class_data.name)
    return {'message': '修改成功', 'data': {'class_id': id}}


@users_router.get("/user/class_view")  # 查看管理员所能操作的所有班级(未添加权限认证)
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
    return {'message': '学院如下', 'pageIndex': pageNow, "pageSize": pageSize, "totalNum": len(all_class),
            "rows": class_data}
