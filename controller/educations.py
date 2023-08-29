import json

from fastapi import APIRouter
from fastapi import Request, Depends

from Celery.add_operation import add_operation
from service.user import SessionModel, OperationModel
from service.education import SchoolModel, CollegeModel, MajorModel, ClassModel

from type.functions import make_parameters
from type.page import page
from type.user import school_interface, class_interface, college_interface, major_interface
from utils.auth_login import auth_login
from utils.response import user_standard_response, page_response, makePageResult

users_router = APIRouter()
session_model = SessionModel()
school_model = SchoolModel()
college_model = CollegeModel()
major_model = MajorModel()
class_model = ClassModel()
operation_model = OperationModel()


def verify_education_by_id(school_id: int = None, college_id: int = None, major_id: int = None, class_id: int = None):
    if school_id is not None:
        exist_school = school_model.get_school_exist_by_id(school_id)
        if exist_school is None:
            return 1
    if college_id is not None:
        exist_college = college_model.get_college_exist_by_id(college_id)
        if exist_college is None:
            return 1
    if major_id is not None:
        exist_major = major_model.get_major_exist_by_id(major_id)
        if exist_major is None:
            return 1
    if class_id is not None:
        exist_class = class_model.get_class_exist_by_id(class_id)
        if exist_class is None:
            return 1
    return 0


@users_router.post("/school_add")  # 管理员添加学校(未添加权限认证)
@user_standard_response
async def user_school_add(request: Request, school_data: school_interface, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    exist_school_name = school_model.get_school_status_by_name(school_data.name)
    str = ''
    if exist_school_name is not None:
        if exist_school_name[0] == 0:
            return {'message': '学校名已存在', 'code': 1, 'data': False}
        else:
            school_model.update_school_status_by_id(exist_school_name[1])
            str = '管理员恢复一个曾删除的学校'
            id = exist_school_name[1]
    else:
        id = school_model.add_school(school_data)
        str = '管理员通过输入学校名称和学校简称添加一个学校'
    parameters = await make_parameters(request)
    add_operation.delay(1, None, str, parameters, session['user_id'])
    return {'message': '添加成功', 'code': 0, 'data': True}


@users_router.get("/school_view")  # 查看管理员所能操作的所有学校(未添加权限认证)
@page_response
async def user_school_view(pageNow: int, pageSize: int):
    # 判断是否有权限
    # 如果有权限
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_school = school_model.get_school_by_admin(Page)  # 以分页形式返回
    result = {'rows':None}
    if all_school != []:
        school_data = []
        for school in all_school:
            temp = school_interface()
            temp_dict = temp.model_validate(school).model_dump()
            id = school_model.get_school_id_by_name(temp_dict['name'])[0]
            temp_dict['id'] = id
            school_data.append(temp_dict)
        result = makePageResult(Page, len(all_school), school_data)
    return {'message': '学校如下', "data": result, "code": 0}


@users_router.delete("/school_delete/{school_id}")  # 管理员删除学校(未添加权限认证)
@user_standard_response
async def user_school_delete(request: Request, school_id: int, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(school_id=school_id)
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': code}
    id = school_model.delete_school(school_id)  # 在school表中将这个学校has_delete设为1
    parameters = await make_parameters(request)
    add_operation.delay(1, None, '管理员通过选择学校来删除一个学校', parameters, session['user_id'])
    return {'message': '删除成功', 'data': True, 'code': 0}


@users_router.put("/school_update/{school_id}")  # 管理员修改学校信息(未添加权限认证)
@user_standard_response
async def user_school_update(request: Request, school_id: int, school_data: school_interface,
                             session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限

    code = verify_education_by_id(school_id=school_id)
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    exist_school = school_model.get_school_id_by_name(school_data.name)
    if exist_school is not None and exist_school[0] != school_id:
        return {'message': '学校名字已存在', 'data': False, 'code': 2}
    school_model.update_school_information(school_id, school_data.name, school_data.school_abbreviation)
    parameters = await make_parameters(request)
    add_operation.delay(1, school_id, '管理员通过选择学校来修改学校信息', parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'school_id': school_id}, 'code': 0}


@users_router.post("/college_add")  # 管理员添加学院(未添加权限认证)
@user_standard_response
async def user_college_add(request: Request, college_data: college_interface, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(school_id=college_data.school_id)
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    college = college_model.get_college_status_by_name(college_data)
    str = ''
    if college is not None:
        if college[0] == 0:
            return {'message': '该校已有该学院', 'data': False, 'code': 2}
        else:
            college_model.update_college_status_by_id(college[1])
            str = '管理员恢复一个曾删除的学院'
            id = college[1]
    else:
        id = college_model.add_college(college_data)
        str = '管理员通过选择学校和输入学院名称添加一个学院'
    parameters = await make_parameters(request)
    add_operation.delay(2, id, str, parameters, session['user_id'])
    return {'message': '添加成功', 'data': True, 'code': 0}


@users_router.delete("/college_delete/{college_id}")  # 管理员删除学院(未添加权限认证)
@user_standard_response
async def user_college_delete(request: Request, college_id: int, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(college_id=college_id)
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': code}
    id = college_model.delete_college(college_id)
    parameters = await make_parameters(request)
    add_operation.delay(2, id, '管理员通过选择学院删除一个学院', parameters, session['user_id'])
    return {'message': '删除成功', 'data': True, 'code': 0}


@users_router.get("/college_view")  # 查看管理员所能操作的所有学院(未添加权限认证)
@page_response
async def user_college_view(school_id: int, pageNow: int, pageSize: int):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_college = college_model.get_college_by_school_id(school_id, Page)  # 以分页形式返回
    result = {'rows':None}
    if all_college != []:
        college_data = []
        for college in all_college:
            temp = college_interface()
            temp_dict = temp.model_validate(college).model_dump()
            ttt = college_interface(name=temp_dict['name'], school_id=temp_dict['school_id'])
            id = college_model.get_college_by_name(ttt)[0]
            temp_dict['id'] = id
            temp_dict.pop('school_id')
            college_data.append(temp_dict)
        result = makePageResult(Page, len(all_college), college_data)
    return {'message': '学院如下', 'data': result, 'code': 0}


@users_router.put("/college_update/{college_id}")  # 管理员修改学院信息(未添加权限认证)
@user_standard_response
async def user_college_update(request: Request, college_id: int, college_data: college_interface,
                              session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(college_id=college_id)
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': 1}
    code = verify_education_by_id(school_id=college_data.school_id)
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 2}
    exist_college = college_model.get_college_by_name(college_data)
    if exist_college is not None and exist_college[0] != college_id:
        return {'message': '该学校下的学院名字已存在', 'data': False, 'code': 3}
    college_model.update_college_school_id_name(college_id, college_data.name)
    parameters = await make_parameters(request)
    add_operation.delay(2, college_id, '管理员通过选择学院修改学院信息', parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'college_id': college_id}, 'code': 0}


@users_router.post("/major_add")  # 管理员添加专业(未添加权限认证)
@user_standard_response
async def user_major_add(request: Request, major_data: major_interface, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    school = verify_education_by_id(school_id=major_data.school_id)
    if school == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    college = verify_education_by_id(college_id=major_data.college_id)
    if college == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    major = major_model.get_major_status_by_name(major_data)
    str = ''
    if major is not None:
        if major[0] == 0:
            return {'message': '该学校的该学院已有该专业', 'data': False, 'code': 3}
        else:
            major_model.update_major_status_by_id(major[1])
            id = major[1]
            str = '管理员恢复一个曾删除的专业'
    else:
        id = major_model.add_major(major_data)
        str = '管理员通过选择学校，学院和输入专业名称添加一个专业'
    parameters = await make_parameters(request)
    add_operation.delay(3, id, str, parameters, session['user_id'])
    return {'message': '添加成功', 'data': True, 'code': 0}


@users_router.delete("/major_delete/{major_id}")  # 管理员删除专业(未添加权限认证)
@user_standard_response
async def user_major_delete(request: Request, major_id: int, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(major_id=major_id)
    if code == 1:
        return {'message': '专业不存在', 'data': False, 'code': code}
    id = major_model.delete_major(major_id)
    parameters = await make_parameters(request)
    add_operation.delay(3, id, '管理员通过选择专业删除一个专业', parameters, session['user_id'])
    return {'message': '删除成功', 'data': {'major_id': id}, 'code': 0}


@users_router.get("/major_view")  # 查看管理员所能操作的所有专业(未添加权限认证)
@page_response
async def user_major_view(college_id: int, pageNow: int, pageSize: int):
    # 判断是否有权限
    # 如果有权限
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_major = major_model.get_major_by_college_id(college_id, Page)  # 以分页形式返回
    result = {'rows':None}
    if all_major != []:
        major_data = []
        for major in all_major:  # 遍历查询结果
            temp = major_interface()
            temp_dict = temp.model_validate(major).model_dump()  # 查询出来的结果转字典
            school_id = college_model.get_college_by_id(temp_dict['college_id']).school_id  # 查出school_id
            temp_dict['school_id'] = school_id
            ttt = major_interface(name=temp_dict['name'], school_id=school_id,
                                  college_id=temp_dict['college_id'])  # 初始化一个major_interface
            id = major_model.get_major_by_name(ttt)[0]  # 查找出当major的id
            temp_dict['id'] = id  # 加入到结果里
            temp_dict.pop('school_id')
            temp_dict.pop('college_id')
            major_data.append(temp_dict)
        result = makePageResult(Page, len(all_major), major_data)
    return {'message': '专业如下', "data": result, 'code': 0}


@users_router.put("/major_update/{major_id}")  # 管理员修改专业信息(未添加权限认证)
@user_standard_response
async def user_major_update(request: Request, major_data: major_interface, major_id: int, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(major_id=major_id)
    if code == 1:
        return {'message': '专业不存在', 'data': False, 'code': 1}
    code = verify_education_by_id(college_id=major_data.college_id)
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    code = verify_education_by_id(school_id=major_data.school_id)
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 3}
    exist_major = major_model.get_major_by_name(major_data)
    if exist_major is not None and exist_major[0] != major_id:
        return {'message': '该学校的该学院的该专业已存在', 'data': False, 'code': 4}
    major_model.update_major_information(major_id, major_data.name)
    parameters = await make_parameters(request)
    add_operation.delay(3, major_id, '管理员通过选择专业修改一个专业的信息', parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'major_id': major_id}, 'code': 0}


@users_router.post("/class_add")  # 管理员添加班级(未添加权限认证)
@user_standard_response
async def user_class_add(request: Request, class_data: class_interface, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    school = verify_education_by_id(school_id=class_data.school_id)
    if school == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    college = verify_education_by_id(college_id=class_data.college_id)
    if college == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    clas = class_model.get_class_status_by_name(class_data)
    str = ''
    if clas is not None:
        if clas[0] == 0:
            return {'message': '该学校的该学院已有该班级', 'data': False, 'code': 3}
        else:
            class_model.update_class_status_by_id(clas[1])
            id = clas[1]
            str = '管理员恢复一个曾删除的班级'
    else:
        id = class_model.add_class(class_data)
        str = '管理员通过选择学校，学院和输入班级名称添加一个班级'
    parameters = await make_parameters(request)
    add_operation.delay(4, id, str, parameters, session['user_id'])
    return {'message': '添加成功', 'data': True, 'code': 0}


@users_router.delete("/class_delete/{class_id}")  # 管理员删除班级(未添加权限认证)
@user_standard_response
async def user_class_delete(request: Request, class_id: int, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(class_id=class_id)
    if code == 1:
        return {'message': '班级不存在', 'data': False, 'code': code}
    id = class_model.delete_class(class_id)
    parameters = await make_parameters(request)
    add_operation.delay(4, id, '管理员通过选择班级删除一个班级', parameters, session['user_id'])
    return {'message': '删除成功', 'data': {'class_id': id}, 'code': 0}


@users_router.put("/class_update/{class_id}")  # 管理员修改班级信息(未添加权限认证)
@user_standard_response
async def user_class_update(request: Request, class_id: int, class_data: class_interface, session=Depends(auth_login)):
    # 判断是否有权限
    # 如果有权限
    code = verify_education_by_id(class_id=class_id)
    if code == 1:
        return {'message': '班级不存在', 'data': False, 'code': 1}
    code = verify_education_by_id(college_id=class_data.college_id)
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    code = verify_education_by_id(school_id=class_data.school_id)
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 3}
    exist_class = class_model.get_class_by_name(class_data)
    if exist_class is not None and exist_class[0] != class_id:
        return {'message': '该学校的该学院的该班级已存在', 'data': False, 'code': 4}
    class_model.update_class_information(class_id, class_data.name)
    parameters = await make_parameters(request)
    add_operation.delay(4, class_id, '管理员通过选择班级修改一个班级的信息', parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'class_id': class_id}, 'code': 0}


@users_router.get("/class_view")  # 查看管理员所能操作的所有班级(未添加权限认证)
@page_response
async def user_class_view(college_id: int, pageNow: int, pageSize: int):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_class = class_model.get_class_by_college_id(college_id, Page)  # 以分页形式返回
    result = {'rows':None}
    if all_class != []:
        class_data = []
        for clas in all_class:  # 遍历查询结果
            temp = class_interface()
            temp_dict = temp.model_validate(clas).model_dump()  # 查询出来的结果转字典
            school_id = college_model.get_college_by_id(temp_dict['college_id']).school_id  # 查出school_id
            temp_dict['school_id'] = school_id
            ttt = class_interface(name=temp_dict['name'], school_id=school_id,
                                  college_id=temp_dict['college_id'])  # 初始化一个class_interface
            id = class_model.get_class_by_name(ttt)[0]  # 查找出当class的id
            temp_dict['id'] = id  # 加入到结果里
            temp_dict.pop('school_id')
            temp_dict.pop('college_id')
            class_data.append(temp_dict)
        result = makePageResult(Page, len(all_class), class_data)
    return {'message': '班级如下', 'data': result, 'code': 0}


@users_router.get("/user_add_education")  # 管理员添加用户时选择用户的学校信息(未添加权限认证)
@page_response
async def user_add_education(school_id: int = None, college_id: int = None, type: int = None,
                             pageNow: int = None, pageSize: int = None, session=Depends(auth_login)):
    if school_id is None and college_id is None:
        result = await user_school_view(pageNow, pageSize)
        ans = json.loads(result.body)
        return ans
    if school_id is not None:
        result = await user_college_view(school_id, pageNow, pageSize)
        ans = json.loads(result.body)
        return ans
    if college_id is not None:
        if type == 0:
            result = await user_major_view(college_id, pageNow, pageSize)
            ans = json.loads(result.body)
            return ans
        elif type == 1:
            result = await user_class_view(college_id, pageNow, pageSize)
            ans = json.loads(result.body)
            return ans
