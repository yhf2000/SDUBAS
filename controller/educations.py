import json
from fastapi import APIRouter
from fastapi import Request, Depends
from Celery.add_operation import add_operation
from service.education import SchoolModel, CollegeModel, MajorModel, ClassModel
from service.user import SessionModel, OperationModel, UserinfoModel, EducationProgramModel, UserModel
from service.file import UserFileModel
from service.permissions import permissionModel
from type.functions import programs_translation, get_user_name, make_parameters, get_url_by_user_file_id
from type.page import page
from type.user import school_interface, class_interface, college_interface, major_interface, education_program_interface
from utils.auth_login import auth_login
from utils.response import user_standard_response, page_response, makePageResult

users_router = APIRouter()
session_model = SessionModel()
school_model = SchoolModel()
college_model = CollegeModel()
major_model = MajorModel()
class_model = ClassModel()
operation_model = OperationModel()
user_info_model = UserinfoModel()
education_program_model = EducationProgramModel()
user_model = UserModel()
user_file_model = UserFileModel()
permission_model = permissionModel()


# 验证学校，学院，专业，班级是否存在的接口。有选择性地传入各个id进行判断
def verify_education_by_id(school_id: int = None, college_id: int = None, major_id: int = None, class_id: int = None):
    if school_id is not None:
        exist_school = school_model.get_school_exist_by_id(school_id)  # 查询学校是否存在
        if exist_school is None:
            return 1
    if college_id is not None:
        exist_college = college_model.get_college_exist_by_id(college_id)  # 查询学院是否存在
        if exist_college is None:
            return 1
    if major_id is not None:
        exist_major = major_model.get_major_exist_by_id(major_id)  # 查询专业是否存在
        if exist_major is None:
            return 1
    if class_id is not None:
        exist_class = class_model.get_class_exist_by_id(class_id)  # 查询班级是否存在
        if exist_class is None:
            return 1
    return 0


# 管理员添加学校:通过输入学校名字，学校简称，上传的学校logo的id新建一个学校。
@users_router.post("/school_add")
@user_standard_response
async def user_school_add(request: Request, school_data: school_interface, session=Depends(auth_login)):
    exist_school_name = school_model.get_school_information_by_name(school_data.name)
    str = ''
    if exist_school_name is not None:  # 首先查看学校是否存在即学校名存在且未被删除
        if exist_school_name.has_delete == 0:
            return {'message': '学校名已存在', 'code': 1, 'data': False}
        else:  # 如果学校名存在但被删除
            school_model.update_school_status_by_id(exist_school_name.id)  # 恢复这个学校
            if school_data.school_abbreviation != exist_school_name.school_abbreviation:  # 学校简称如果变化则进行更新
                school_model.update_school_information(exist_school_name.id, school_data.name,
                                                       school_data.school_abbreviation,None)
            if school_data.school_logo_id != exist_school_name.school_logo_id:  # 学校logo_id如果变化则进行更新
                school_model.update_school_logo(exist_school_name.id, school_data.school_logo_id)
            str = f"用户{session['user_id']}于xxx恢复曾删除学校{school_data.name}"
            id = exist_school_name.id
    else:
        id = school_model.add_school(school_data)
        permission_model.create_work_role(session['user_id'], '学校学生', 1, id)
        str = f"用户{session['user_id']}于xxx添加学校{school_data.name}"
    parameters = await make_parameters(request)
    add_operation.delay(1, id, '添加学校', str, parameters, session['user_id'])
    return {'message': '添加成功', 'code': 0, 'data': True}


# 以分页形式查看管理员所能操作的所有学校
@users_router.get("/school_view")
@page_response
async def user_school_view(pageNow: int, pageSize: int, request:Request, permission=Depends(auth_login)):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_school, counts = school_model.get_school_by_admin(Page)  # 以分页形式返回
    result = {'rows': None}
    if all_school != []:
        school_data = []
        for school in all_school:  # 对每个学校的数据进行处理
            temp = school_interface()
            temp_dict = temp.model_validate(school).model_dump()
            url = get_url_by_user_file_id(request, temp_dict['school_logo_id'])
            temp_dict['image'] = url[temp_dict['school_logo_id']]['url']
            id = school_model.get_school_id_by_name(temp_dict['name'])[0]
            temp_dict['id'] = id
            school_data.append(temp_dict)
        result = makePageResult(Page, counts, school_data)
    parameters = await make_parameters(request)
    add_operation.delay(1, None, '查看学校', f"用户{permission['user_id']}于xxx查看所有学校", parameters, permission['user_id'])
    return {'message': '学校如下', "data": result, "code": 0}


# 管理员通过学校id删除学校
@users_router.delete("/school_delete/{school_id}")
@user_standard_response
async def user_school_delete(request: Request, school_id: int, session=Depends(auth_login)):
    code = verify_education_by_id(school_id=school_id)  # 查看学校是否存在
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': code}
    school_name = school_model.delete_school(school_id)  # 在school表中将这个学校has_delete设为1
    parameters = await make_parameters(request)
    add_operation.delay(1, school_id, '删除学校', f"用户{session['user_id']}于xxx删除学校{school_name}", parameters,
                        session['user_id'])
    return {'message': '删除成功', 'data': True, 'code': 0}


# 管理员通过输入学校名字和简称修改学校信息
@users_router.put("/school_update/{school_id}")
@user_standard_response
async def user_school_update(request: Request, school_id: int, school_data: school_interface,
                             session=Depends(auth_login)):
    code = verify_education_by_id(school_id=school_id)  # 查看学校是否存在
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    exist_school = school_model.get_school_id_by_name(school_data.name)
    if exist_school is not None and exist_school[0] != school_id:  # 要修改的学校名字已存在
        return {'message': '学校名字已存在', 'data': False, 'code': 2}
    school_model.update_school_information(school_id, school_data.name, school_data.school_abbreviation, school_data.school_logo_id)  # 修改学校信息
    parameters = await make_parameters(request)
    add_operation.delay(1, school_id, '修改学校信息',
                        f"用户{session['user_id']}于xxx修改学校{school_data.name}信息",
                        parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'school_id': school_id}, 'code': 0}


# 管理员添加学院:通过选择学校，输入学院名字，上传的学院logo的id新建一个学院。
@users_router.post("/college_add")
@user_standard_response
async def user_college_add(request: Request, college_data: college_interface, session=Depends(auth_login)):
    code = verify_education_by_id(school_id=college_data.school_id)  # 查看学校是否存在
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    college = college_model.get_college_status_by_name(college_data)  # 查看学院的状态
    str = ''
    if college is not None:  # 该校已有该学院
        if college[0] == 0:
            return {'message': '该校已有该学院', 'data': False, 'code': 2}
        else:  # 将被删除的学院恢复
            college_model.update_college_status_by_id(college[1])
            str = f"用户{session['user_id']}于xxx恢复曾删除学院{college_data.name}"
            id = college[1]
    else:  # 新建一个学院
        id = college_model.add_college(college_data)
        permission_model.create_work_role(session['user_id'], '学院学生', 2, id)
        str = f"用户{session['user_id']}于xxx添加学院{college_data.name}"
    parameters = await make_parameters(request)
    add_operation.delay(2, id, '添加学院', str, parameters, session['user_id'])
    return {'message': '添加成功', 'data': True, 'code': 0}


# 管理员通过学院id删除学院
@users_router.delete("/college_delete/{college_id}")
@user_standard_response
async def user_college_delete(request: Request, college_id: int, session=Depends(auth_login)):
    code = verify_education_by_id(college_id=college_id)
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': code}
    name = college_model.delete_college(college_id)
    parameters = await make_parameters(request)
    add_operation.delay(2, college_id, '删除学院', f"用户{session['user_id']}于xxx删除学院{name}", parameters,
                        session['user_id'])
    return {'message': '删除成功', 'data': True, 'code': 0}


# 以分页形式查看管理员所能操作的所有学院
@users_router.get("/college_view")
@page_response
async def user_college_view(school_id: int, pageNow: int, pageSize: int, request: Request,
                            permission=Depends(auth_login)):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_college, counts = college_model.get_college_by_school_id(school_id, Page)  # 以分页形式返回
    result = {'rows': None}
    if all_college != []:
        college_data = []
        for college in all_college:  # 对所有学院的信息进行处理
            temp = college_interface()
            temp_dict = temp.model_validate(college).model_dump()
            ttt = college_interface(name=temp_dict['name'], school_id=temp_dict['school_id'])
            id = college_model.get_college_by_name(ttt)[0]
            url = get_url_by_user_file_id(request, temp_dict['college_logo_id'])
            temp_dict['image'] = url[temp_dict['college_logo_id']]['url']
            temp_dict['id'] = id
            temp_dict.pop('school_id')
            college_data.append(temp_dict)
        result = makePageResult(Page, counts, college_data)
    parameters = await make_parameters(request)
    add_operation.delay(2, None, '查看学院', f"用户{permission['user_id']}于xxx查看所有学院", parameters, permission['user_id'])
    return {'message': '学院如下', 'data': result, 'code': 0}


# 管理员通过学院id修改学院名字
@users_router.put("/college_update/{college_id}")
@user_standard_response
async def user_college_update(request: Request, college_id: int, college_data: college_interface,
                              session=Depends(auth_login)):
    code = verify_education_by_id(college_id=college_id)  # 查看学院是否存在
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': 1}
    code = verify_education_by_id(school_id=college_data.school_id)  # 查看学校是否存在
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 2}
    exist_college = college_model.get_college_by_name(college_data)
    if exist_college is not None and exist_college[0] != college_id:
        return {'message': '该学校下的学院名字已存在', 'data': False, 'code': 3}
    college_model.update_college_school_id_name(college_id, college_data.name, college_data.college_logo_id)
    parameters = await make_parameters(request)
    add_operation.delay(2, college_id, '修改学院信息',
                        f"用户{session['user_id']}于xxx修改学院{college_data.name}信息",
                        parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'college_id': college_id}, 'code': 0}


# 管理员添加专业:通过选择学校，选择学院，输入专业名字新建一个专业。
@users_router.post("/major_add")
@user_standard_response
async def user_major_add(request: Request, major_data: major_interface, session=Depends(auth_login)):
    school = verify_education_by_id(school_id=major_data.school_id)  # 查看学校是否存在
    if school == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    college = verify_education_by_id(college_id=major_data.college_id)  # 查看学院是否存在
    if college == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    major = major_model.get_major_status_by_name(major_data)
    str = ''
    if major is not None:
        if major[0] == 0:  # 该学校的该学院已有该专业
            return {'message': '该学校的该学院已有该专业', 'data': False, 'code': 3}
        else:  # 恢复一个曾删除的专业
            major_model.update_major_status_by_id(major[1])
            id = major[1]
            str = f"用户{session['user_id']}于xxx恢复曾删除专业{major_data.name}"
            education_program_model.update_education_program_exist(id)
    else:  # 新建一个专业
        id = major_model.add_major(major_data)
        permission_model.create_work_role(session['user_id'], '专业学生', 3, id)
        programs = major_data.education_program
        new_programs = {}
        # 遍历原始的 programs 字典
        for old_key, value in programs.items():
            # 使用 programs_translation 字典来映射中英文课程名称
            new_key = programs_translation.get(old_key, old_key)
            new_programs[new_key] = value
        # 现在，new_programs 字典包含了映射后的数据
        programs = new_programs
        programs['major_id'] = id
        new_program = education_program_interface(**programs)
        id1 = education_program_model.add_education_program(new_program)
        str = f"用户{session['user_id']}于xxx添加专业{major_data.name}并上传培养方案"
    parameters = await make_parameters(request)
    add_operation.delay(3, id, '添加专业', str, parameters, session['user_id'])
    return {'message': '添加成功', 'data': True, 'code': 0}


# 管理员通过专业id删除专业
@users_router.delete("/major_delete/{major_id}")
@user_standard_response
async def user_major_delete(request: Request, major_id: int, session=Depends(auth_login)):
    code = verify_education_by_id(major_id=major_id)  # 查看专业是否存在
    if code == 1:
        return {'message': '专业不存在', 'data': False, 'code': code}
    names = major_model.delete_major(major_id)
    education_program_model.delete_education_program(names[0])
    parameters = await make_parameters(request)
    add_operation.delay(3, names[0], '删除学院', f"用户{session['user_id']}于xxx删除专业{names[1]}", parameters,
                        session['user_id'])
    return {'message': '删除成功', 'data': {'major_id': names[0]}, 'code': 0}


# 以分页形式查看管理员所能操作的所有专业
@users_router.get("/major_view")
@page_response
async def user_major_view(college_id: int, pageNow: int, pageSize: int, request: Request,
                          permission=Depends(auth_login)):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_major, counts = major_model.get_major_by_college_id(college_id, Page)  # 以分页形式返回
    result = {'rows': None}
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
    parameters = await make_parameters(request)
    add_operation.delay(3, None, '查看专业', f"用户{permission['user_id']}于xxx查看所有专业", parameters, permission['user_id'])
    return {'message': '专业如下', "data": result, 'code': 0}


# 管理员通过专业id修改专业名字
@users_router.put("/major_update/{major_id}")
@user_standard_response
async def user_major_update(request: Request, major_data: major_interface, major_id: int, session=Depends(auth_login)):
    code = verify_education_by_id(major_id=major_id)  # 查看专业是否存在
    if code == 1:
        return {'message': '专业不存在', 'data': False, 'code': 1}
    code = verify_education_by_id(college_id=major_data.college_id)  # 查看学院是否存在
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    code = verify_education_by_id(school_id=major_data.school_id)  # 查看学校是否存在
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 3}
    exist_major = major_model.get_major_by_name(major_data)
    if exist_major is not None and exist_major[0] != major_id:  # 要修改为的专业名字已存在
        return {'message': '该学校的该学院的该专业已存在', 'data': False, 'code': 4}
    major_model.update_major_information(major_id, major_data.name)  # 修改专业名
    if major_data.education_program is not None:
        education_program_model.delete_education_program_by_major_id(major_id)
        programs = major_data.education_program
        new_programs = {}
        # 遍历原始的 programs 字典
        for old_key, value in programs.items():
            # 使用 programs_translation 字典来映射中英文课程名称
            new_key = programs_translation.get(old_key, old_key)
            new_programs[new_key] = value
        # 现在，new_programs 字典包含了映射后的数据
        programs = new_programs
        programs['major_id'] = id
        new_program = education_program_interface(**programs)
        id1 = education_program_model.add_education_program(new_program)
    parameters = await make_parameters(request)
    add_operation.delay(3, major_id, '修改专业信息',
                        f"用户{session['user_id']}于xxx修改专业信息",
                        parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'major_id': major_id}, 'code': 0}


# 管理员添加班级:通过选择学校，选择学院，输入班级专业名字新建一个班级。
@users_router.post("/class_add")
@user_standard_response
async def user_class_add(request: Request, class_data: class_interface, session=Depends(auth_login)):
    school = verify_education_by_id(school_id=class_data.school_id)  # 查看学校是否存在
    if school == 1:
        return {'message': '学校不存在', 'data': False, 'code': 1}
    college = verify_education_by_id(college_id=class_data.college_id)  # 查看学院是否存在
    if college == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    clas = class_model.get_class_status_by_name(class_data)  # 查看班级是否存在
    str = ''
    if clas is not None:
        if clas[0] == 0:  # 该学校的该学院已有该班级
            return {'message': '该学校的该学院已有该班级', 'data': False, 'code': 3}
        else:  # 管理员恢复一个曾删除的班级
            class_model.update_class_status_by_id(clas[1])
            id = clas[1]
            str = f"用户{session['user_id']}于xxx恢复曾删除班级{class_data.name}"
    else:  # 新建一个班级
        id = class_model.add_class(class_data)
        permission_model.create_work_role(session['user_id'], '班级学生', 4, id)
        str = f"用户{session['user_id']}于xxx添加班级{class_data.name}"
    parameters = await make_parameters(request)
    add_operation.delay(4, id, '添加班级', str, parameters, session['user_id'])
    return {'message': '添加成功', 'data': True, 'code': 0}


# 管理员通过班级id班级
@users_router.delete("/class_delete/{class_id}")
@user_standard_response
async def user_class_delete(request: Request, class_id: int, session=Depends(auth_login)):
    code = verify_education_by_id(class_id=class_id)  # 查询班级是否存在
    if code == 1:
        return {'message': '班级不存在', 'data': False, 'code': code}
    name = class_model.delete_class(class_id)
    parameters = await make_parameters(request)
    add_operation.delay(4, class_id, '删除班级', f"用户{session['user_id']}在xxx删除班级{name}", parameters,
                        session['user_id'])
    return {'message': '删除成功', 'data': {'class_id': class_id}, 'code': 0}


# 管理员通过班级id修改班级信息
@users_router.put("/class_update/{class_id}")
@user_standard_response
async def user_class_update(request: Request, class_id: int, class_data: class_interface, session=Depends(auth_login)):
    code = verify_education_by_id(class_id=class_id)  # 查看班级是否存在
    if code == 1:
        return {'message': '班级不存在', 'data': False, 'code': 1}
    code = verify_education_by_id(college_id=class_data.college_id)  # 查看学院是否存在
    if code == 1:
        return {'message': '学院不存在', 'data': False, 'code': 2}
    code = verify_education_by_id(school_id=class_data.school_id)  # 查看学校是否存在
    if code == 1:
        return {'message': '学校不存在', 'data': False, 'code': 3}
    exist_class = class_model.get_class_by_name(class_data)
    if exist_class is not None and exist_class[0] != class_id:  # 要修改的班级名已存在
        return {'message': '该学校的该学院的该班级已存在', 'data': False, 'code': 4}
    class_model.update_class_information(class_id, class_data.name)  # 进行修改
    parameters = await make_parameters(request)
    add_operation.delay(4, class_id, '修改班级信息',
                        f"用户{session['user_id']}于xxx修改班级信息",
                        parameters, session['user_id'])
    return {'message': '修改成功', 'data': {'class_id': class_id}, 'code': 0}


# 查看管理员所能操作的所有班级
@users_router.get("/class_view")
@page_response
async def user_class_view(college_id: int, pageNow: int, pageSize: int, request: Request,
                          permission=Depends(auth_login)):
    Page = page(pageSize=pageSize, pageNow=pageNow)
    all_class, counts = class_model.get_class_by_college_id(college_id, Page)  # 以分页形式返回
    result = {'rows': None}
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
    parameters = await make_parameters(request)
    add_operation.delay(4, None, '查看班级', f"用户{permission['user_id']}于xxx查看所有班级", parameters, permission['user_id'])
    return {'message': '班级如下', 'data': result, 'code': 0}


@users_router.get("/user_add_education")
@page_response
async def user_add_education(school_id: int = None, college_id: int = None, type: int = None,
                             pageNow: int = None, pageSize: int = None):
    if school_id is None and college_id is None:  # 此时查看所有学校的信息
        result = await user_school_view(pageNow, pageSize)
        ans = json.loads(result.body)
        return ans
    if school_id is not None:  # 此时查看该学校所有学院的信息
        result = await user_college_view(school_id, pageNow, pageSize)
        ans = json.loads(result.body)
        return ans
    if college_id is not None:
        if type == 0:  # 此时查看该学院所有专业的信息
            result = await user_major_view(college_id, pageNow, pageSize)
            ans = json.loads(result.body)
            return ans
        elif type == 1:  # 此时查看该学院所有班级的信息
            result = await user_class_view(college_id, pageNow, pageSize)
            ans = json.loads(result.body)
            return ans


@users_router.get("/user_school_get")
@user_standard_response
async def user_school_get(request: Request,session=Depends(auth_login)):
    school_id = permission_model.search_given_role(session['user_id'], 0)
    school_logo_id = school_model.get_school_logo_id_by_id(school_id)
    school_logo_id = school_model.get_school_logo_id_by_name('山东大学')[0] if school_logo_id is None else school_logo_id[0]
    url = get_url_by_user_file_id(request,school_logo_id)
    return {'message': '图片如下', 'data': url, 'code': 0}