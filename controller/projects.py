from fastapi import APIRouter, Depends, Query, Request
from type.functions import make_parameters
from service.project import ProjectService
from type.project import CreditCreate, SubmissionCreate, ScoreCreate, \
    ProjectUpdate, ProjectCreate, user_submission, SubmissionListCreate, project_content_renew
from utils.auth_login import auth_login
from utils.auth_permission import auth_permission, auth_permission_default
from utils.response import standard_response, makePageResult
from type.page import page
from Celery.add_operation import add_operation

projects_router = APIRouter()

project_service = ProjectService()


@projects_router.post("/")
@standard_response
async def create_project(request: Request, project: ProjectCreate, user=Depends(auth_permission_default)) -> int:
    results = project_service.create_project(project, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, results, "添加项目", parameters, user['user_id'])
    return results


@projects_router.put("/update/{project_id}")
@standard_response
async def update_project(request: Request, project_id: int, project: ProjectUpdate, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.update_project(project_id=project_id, newproject=project, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "更新项目", parameters, user['user_id'])
    return results


@projects_router.delete("/delete/{project_id}")
@standard_response
async def delete_project(request: Request, project_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.delete_project(project_id=project_id, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "删除项目", parameters, user['user_id'])
    return results


@projects_router.get("/list")
@standard_response
async def list_projects(request: Request,
                        pageNow: int = Query(description="页码", gt=0),
                        pageSize: int = Query(description="每页数量", gt=0), user=Depends(auth_permission_default)):
    user_id = user['user_id']
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.list_projects(pg=Page, user_id=user_id)  # 返回总额，分页数据
    parameters = await make_parameters(request)
    add_operation.delay(7, 0, "查看项目列表", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数
    # 实现查询项目列表的逻辑


@projects_router.get("/get/{project_id}")
@standard_response
async def get_project(request: Request, project_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.get_project(project_id=project_id, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看某一项目", parameters, user['user_id'])
    return results
    # 实现查询某一项目


@projects_router.get("/contents/{project_id}")
@standard_response
async def get_project_content(request: Request, project_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.list_projects_content(project_id=project_id, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看项目内容列表", parameters, user['user_id'])
    return results
    # 实现查询项目内容结构表的逻辑


@projects_router.get("/{project_id}/contents/{content_id}")
@standard_response
async def get_specific_project_content(request: Request, project_id: int, content_id: int,
                                       user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    results = project_service.get_projects_content(content_id=content_id, project_id=project_id,
                                                   user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看某一项目内容", parameters, user['user_id'])
    return results
    # 查看某一项目内容


@projects_router.post("/credits/{project_id}")
@standard_response
async def add_project_credit(request: Request, project_id: int, credit: CreditCreate, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.create_credit(credit=credit, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "添加项目学分认定", parameters, user['user_id'])
    return results
    # 实现添加项目学分认定的逻辑


@projects_router.post("/submissions/{project_id}/contents/{content_id}")
@standard_response
async def submit_project_content(request: Request, project_id: int, content_id: int, submission: SubmissionListCreate,
                                 user=Depends(auth_permission)):
    # 可能需要增加对提交权限的处理
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    results = project_service.create_submission(submission=submission, user_id=user['user_id'], project_id=project_id)
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "增加项目提交要求", parameters, user['user_id'])
    return results
    # 实现提交项目要求内容的逻辑


@projects_router.post("/scores/{project_id}/contents/{content_id}")
@standard_response
async def score_project_content(request: Request, project_id: int, content_id: int, score: ScoreCreate,
                                user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    score.judger = user['user_id']
    score.user_pcs_id = content_id
    results = project_service.create_score(scoremodel=score, user_id=user['user_id'], project_id=project_id)
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "对项目内容打分", parameters, user['user_id'])
    return results
    # 实现对项目内容打分的逻辑


@projects_router.get("/submissions/{project_id}/contents/{content_id}")
@standard_response
async def view_user_submission(request: Request, project_id: int, content_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    results = project_service.get_user_submission_list(project_id=project_id, content_id=content_id,
                                                       user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看用户提交", parameters, user['user_id'])
    return results
    # 实现查看用户在一个内容下的提交内容的逻辑


@projects_router.get("/members/{project_id}")
@standard_response
async def list_project_members(request: Request, project_id: int,
                               pageNow: int = Query(description="页码", gt=0),
                               pageSize: int = Query(description="每页数量", gt=0),
                               user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_user_by_project_id(project_id=project_id, pg=Page, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看参加项目学生", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)
    # 查询参加项目学生


@projects_router.post("/submit/{project_id}/contents/{content_id}")
@standard_response
async def create_user_submission(request: Request, project_id: int, content_id: int,
                                 User_submission: user_submission, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    User_submission.user_id = user['user_id']
    results = project_service.create_user_submission(uer_submission=User_submission, user_id=user['user_id'],
                                                     project_id=project_id)
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "用户提交", parameters, user['user_id'])
    return results
    # 实现用户提交的逻辑


@projects_router.get("/progress/{project_id}")
@standard_response
async def create_user_submission(request: Request, project_id: int,
                                 user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.get_project_progress(project_id=project_id, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看项目进度", parameters, user['user_id'])
    return results
    # 实现查询项目进度的逻辑


@projects_router.get("/score/{project_id}")
@standard_response
async def create_user_submission(request: Request, project_id: int,
                                 user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.get_user_project_score(project_id=project_id, user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看项目成绩", parameters, user['user_id'])
    return results
    # 实现查询项目成绩的逻辑


@projects_router.get("/project/type")
@standard_response
async def list_projects(request: Request, projectType: str = Query(),
                        tag: str = Query(),
                        pageNow: int = Query(description="页码", gt=0),
                        pageSize: int = Query(description="每页数量", gt=0), user=Depends(auth_permission_default)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_projects_by_type(project_type=projectType, pg=Page, tags=tag,
                                                   user_id=user['user_id'])  # 返回总额，分页数据
    parameters = await make_parameters(request)
    add_operation.delay(7, 0, "查看某类项目", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数
    # 实现分类查询项目列表的逻辑


@projects_router.get("/content/submission/{project_id}")
@standard_response
async def list_projects(request: Request, project_id: int,
                        contentId: int = Query(description="每页数量", gt=0),
                        pageNow: int = Query(description="页码", gt=0),
                        pageSize: int = Query(description="每页数量", gt=0),
                        user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_content_by_projectcontentid_userid(user_id=user['user_id'],
                                                                     content_id=contentId,
                                                                     pg=Page, project_id=project_id)  # 返回总额，分页数据
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看项目内容提交项", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数
    # 查看项目内容提交项


@projects_router.put("/renew/{project_id}/content")
@standard_response
async def renew_project(request: Request, project_id: int, project_content: project_content_renew,
                        user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    results = project_service.renew_project_content(project_id=project_id, project_contents=project_content,
                                                    user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "更新项目内容", parameters, user['user_id'])
    return results


@projects_router.get("/user/credits")  # 没改好
@standard_response
async def get_user_credits(request: Request, user=Depends(auth_permission_default)):
    results = project_service.get_credits_user_get(user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, 0, "查询学分", parameters, user['user_id'])
    return results
    # 查询学分


@projects_router.get("/{project_id}/user/score/all")
@standard_response
async def get_all_projects_score(request: Request, project_id: int,
                                 pageNow: int = Query(description="页码", gt=0),
                                 pageSize: int = Query(description="每页数量", gt=0),
                                 user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    project_service.check_project_exist(project_id=project_id)
    tn, results = project_service.get_all_project_score(project_id=project_id, user_id=user['user_id'], pg=Page)
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看用户项目内容成绩", parameters, user['user_id'])
    return makePageResult(Page, tn, results)


@projects_router.get("/content/{project_id}/{content_id}/score/all")
@standard_response
async def get_all_content_user_score(request: Request, project_id: int, content_id: int,
                                     pageNow: int = Query(description="页码", gt=0),
                                     pageSize: int = Query(description="每页数量", gt=0),
                                     user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_content_user_score_all(project_id=project_id, content_id=content_id, pg=Page,
                                                         user_id=user['user_id'])
    parameters = await make_parameters(request)
    add_operation.delay(7, project_id, "查看某项目内容所有用户成绩", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数


@projects_router.get("/user/credits/all")
@standard_response
async def get_all_content_user_score(request: Request,
                                     pageNow: int = Query(description="页码", gt=0),
                                     pageSize: int = Query(description="每页数量", gt=0),
                                     user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, results = project_service.get_user_credit_all(user_id=user['user_id'], pg=Page)
    parameters = await make_parameters(request)
    add_operation.delay(0, 0, "查看用户学分明细", parameters, user['user_id'])
    return makePageResult(pg=Page, tn=tn, data=results)
