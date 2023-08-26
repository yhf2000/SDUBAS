from fastapi import APIRouter, Depends, Query, Request

from service.project import ProjectService
from type.project import CreditCreate, SubmissionCreate, ScoreCreate, \
    ProjectUpdate, ProjectCreate, user_submission, SubmissionListCreate, project_content_renew
from utils.auth_login import auth_login
from utils.auth_permission import auth_permission
from utils.response import standard_response, makePageResult
from type.page import page

projects_router = APIRouter()

project_service = ProjectService()


@projects_router.post("/")
@standard_response
async def create_project(project: ProjectCreate, user=Depends(auth_permission)) -> int:
    return project_service.create_project(project, user_id=user)


@projects_router.put("/{project_id}")
@standard_response
async def update_project(project_id: int, project: ProjectUpdate, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.update_project(project_id=project_id, newproject=project, user_id=user)


@projects_router.delete("/{project_id}")
@standard_response
async def delete_project(project_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.delete_project(project_id=project_id, user_id=user)


@projects_router.get("/")
@standard_response
async def list_projects(pageNow: int = Query(description="页码", gt=0),
                        pageSize: int = Query(description="每页数量", gt=0), user=Depends(auth_permission)):
    user_id = user
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.list_projects(pg=Page, user_id=user_id)  # 返回总额，分页数据
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数
    # 实现查询项目列表的逻辑


@projects_router.get("/{project_id}")
@standard_response
async def get_project(project_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.get_project(project_id=project_id, user_id=user)
    # 实现查询某一项目


@projects_router.get("/{project_id}/contents")
@standard_response
async def get_project_content(project_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.list_projects_content(project_id=project_id, user_id=user)
    # 实现查询项目内容结构表的逻辑


@projects_router.get("/{project_id}/contents/{content_id}")
@standard_response
async def get_specific_project_content(project_id: int, content_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    return project_service.get_projects_content(content_id=content_id, project_id=project_id, user_id=user)


@projects_router.post("/{project_id}/credits")
@standard_response
async def add_project_credit(project_id: int, credit: CreditCreate, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.create_credit(credit=credit, user_id=user)
    # 实现添加项目学分认定的逻辑


@projects_router.post("/{project_id}/contents/{content_id}/submissions")
@standard_response
async def submit_project_content(project_id: int, content_id: int, submission: SubmissionListCreate,
                                 user=Depends(auth_permission)):
    # 可能需要增加对提交权限的处理
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    return project_service.create_submission(submission=submission, user_id=user, project_id=project_id)
    # 实现提交项目要求内容的逻辑


@projects_router.post("/{project_id}/contents/{content_id}/scores")
@standard_response
async def score_project_content(project_id: int, content_id: int, score: ScoreCreate, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    score.judger = user
    return project_service.create_score(scoremodel=score, user_id=user, project_id=project_id)
    # 实现对项目内容打分的逻辑


@projects_router.get("/{project_id}/contents/{content_id}/submissions")
@standard_response
async def view_user_submission(project_id: int, content_id: int, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    return project_service.get_user_submission_list(project_id=project_id, content_id=content_id, user_id=user)
    # 实现查看用户在一个内容下的提交内容的逻辑


@projects_router.get("/{project_id}/members")
@standard_response
async def list_project_members(project_id: int,
                               pageNow: int = Query(description="页码", gt=0),
                               pageSize: int = Query(description="每页数量", gt=0),
                               user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_user_by_project_id(project_id=project_id, pg=Page, user_id=user)
    return makePageResult(pg=Page, tn=tn, data=res)


@projects_router.post("/{project_id}/contents/{content_id}/submit")
@standard_response
async def create_user_submission(project_id: int, content_id: int,
                                 User_submission: user_submission, user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    User_submission.user_id = user
    return project_service.create_user_submission(uer_submission=User_submission, user_id=user, project_id=project_id)
    # 实现用户提交的逻辑


@projects_router.get("/{project_id}/progress")
@standard_response
async def create_user_submission(project_id: int,
                                 user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.get_project_progress(project_id=project_id, user_id=user)
    # 实现查询项目进度的逻辑


@projects_router.get("/{project_id}/score")
@standard_response
async def create_user_submission(project_id: int,
                                 user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.get_user_project_score(project_id=project_id, user_id=user)
    # 实现查询项目成绩的逻辑


@projects_router.get("/project/type")
@standard_response
async def list_projects(projectType: str = Query(),
                        tag: str = Query(),
                        pageNow: int = Query(description="页码", gt=0),
                        pageSize: int = Query(description="每页数量", gt=0), user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_projects_by_type(project_type=projectType, pg=Page, tags=tag,
                                                   user_id=user)  # 返回总额，分页数据
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数
    # 实现分类查询项目列表的逻辑


@projects_router.get("/{project_id}/Content/submission")
@standard_response
async def list_projects(project_id: int,
                        contentId: int = Query(description="每页数量", gt=0),
                        pageNow: int = Query(description="页码", gt=0),
                        pageSize: int = Query(description="每页数量", gt=0),
                        user=Depends(auth_permission)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_content_by_projectcontentid_userid(user_id=user,
                                                                     content_id=contentId,
                                                                     pg=Page, project_id=project_id)  # 返回总额，分页数据
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数


@projects_router.put("/renew/{project_id}/content")
@standard_response
async def renew_project(project_id: int, project_content: project_content_renew,
                        user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.renew_project_content(project_id=project_id, project_contents=project_content, user_id=user)


@projects_router.get("/user/credits")
@standard_response
async def get_user_credits(user=Depends(auth_permission)):
    return project_service.get_credits_user_get(user_id=user)


@projects_router.get("/user/{project_id}/score/all")
@standard_response
async def get_all_projects_score(project_id: int,
                                 user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    return project_service.get_all_project_score(project_id=project_id, user_id=user)


@projects_router.get("/content/{project_id}/{content_id}/score/all")
@standard_response
async def get_all_content_user_score(project_id: int, content_id: int,
                                     pageNow: int = Query(description="页码", gt=0),
                                     pageSize: int = Query(description="每页数量", gt=0),
                                     user=Depends(auth_permission)):
    project_service.check_project_exist(project_id=project_id)
    project_service.check_projectContent_exist(project_id=project_id, content_id=content_id)
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.get_content_user_score_all(project_id=project_id, content_id=content_id, pg=Page,
                                                         user_id=user)
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数
