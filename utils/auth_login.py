import json

from fastapi import Request, HTTPException, Header

from model.db import session_db
from service.user import UserModel, SchoolModel, CollegeModel, MajorModel, ClassModel
from type.user import register_interface, school_interface, \
    college_interface, major_interface, class_interface, login_interface
from utils.response import user_standard_response

def auth_login(request: Request):  # 用来判断用户是否登录
    token = request.cookies.get("SESSION")
    if token is not None:
        session = session_db.get(token)  # 有效session中没有
        if session is None:
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


def auth_not_login(request: Request):  # 用来判断用户是否登录
    token = request.cookies.get("SESSION")
    if token is None:
        return token
    user = session_db.get(token)  # 有效session中有
    if user is not None and json.loads(user)['func_type'] == 0:
        raise HTTPException(
            status_code=401,
            detail="用户已登录"
        )
    elif user is not None:
        user = json.loads(user)
        user_id = user['user_id']
        db = UserModel()
        status = db.get_user_status_by_user_id(int(user_id))[0]
        if status == 2:
            raise HTTPException(
                status_code=401,
                detail="账号已注销"
            )
        elif status == 3:
            raise HTTPException(
                status_code=401,
                detail="账号被封禁"
            )
    return token  # 没登陆且账号状态无异常就返回用户的token




def auth_major_exist(major_data: major_interface):  # 判断major是否存在
    db = SchoolModel()
    db1 = CollegeModel()
    db2 = MajorModel()
    school = db.get_school_by_id(major_data.school_id)
    if school is None:
        raise HTTPException(
            status_code=404,
            detail="没有该学校"
        )
    college = db1.get_college_by_id(major_data.college_id)
    if college is None or college.school_id != major_data.school_id:
        raise HTTPException(
            status_code=404,
            detail="没有该学院"
        )
    major = db2.get_major_by_name(major_data)
    if major is not None:
        raise HTTPException(
            status_code=404,
            detail="已有该学校,该学院的该专业"
        )
    return major_data



def auth_class_exist(class_data: class_interface):  # 判断class是否存在
    db = SchoolModel()
    db1 = CollegeModel()
    db2 = ClassModel()
    school = db.get_school_by_id(class_data.school_id)
    if school is None:
        raise HTTPException(
            status_code=404,
            detail="没有该学校"
        )
    college = db1.get_college_by_id(class_data.college_id)
    if college is None or college.school_id != class_data.school_id:
        raise HTTPException(
            status_code=404,
            detail="没有该班级"
        )
    clas = db2.get_class_by_name(class_data)
    if clas is not None:
        raise HTTPException(
            status_code=404,
            detail="已有该学校,该学院的该班级"
        )
    return class_data


def auth_class_not_exist(class_id: int):  # 判断class是否存在
    db = ClassModel()
    exist_class = db.get_class_by_id(class_id)
    if exist_class is None:
        raise HTTPException(
            status_code=404,
            detail="没有该班级"
        )
    return class_id
