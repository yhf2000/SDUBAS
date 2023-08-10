from fastapi import APIRouter, Depends, Query

from service.project import ProjectService
from type.project import CreditCreate, SubmissionCreate, ScoreCreate, ProjectUpdate, ProjectCreate, user_submission
from utils.auth_login import auth_login
from utils.response import standard_response, makePageResult
from type.page import page

projects_router = APIRouter()

project_service = ProjectService()


@projects_router.post("/")
@standard_response
async def create_project(project: ProjectCreate, user=Depends(auth_login)) -> int:
    return project_service.create_project(project)


@projects_router.put("/{project_id}")
@standard_response
async def update_project(project_id: int, project: ProjectUpdate, user=Depends(auth_login)):
    return project_service.update_project(project_id=project_id, newproject=project)


@projects_router.delete("/{project_id}")
@standard_response
async def delete_project(project_id: int, user=Depends(auth_login)):
    return project_service.delete_project(project_id=project_id)


@projects_router.get("/")
@standard_response
async def list_projects(pageNow: int = Query(description="页码", gt=0),
                        pageSize: int = Query(description="每页数量", gt=0), user=Depends(auth_login)):
    Page = page(pageNow=pageNow, pageSize=pageSize)
    tn, res = project_service.list_projects(pg=Page)  # 返回总额，分页数据
    return makePageResult(pg=Page, tn=tn, data=res)  # 封装的函数
    # 实现查询项目列表的逻辑


@projects_router.get("/{project_id}")
@standard_response
async def get_project(project_id: int, user=Depends(auth_login)):
    return project_service.get_project(project_id=project_id)
    # 实现查询某一项目


@projects_router.get("/{project_id}/contents")
@standard_response
async def get_project_content(project_id: int, user=Depends(auth_login)):
    return project_service.list_projects_content(project_id=project_id)
    # 实现查询项目内容结构表的逻辑


@projects_router.get("/{project_id}/contents/{content_id}")
@standard_response
async def get_specific_project_content(project_id: int, content_id: int, user=Depends(auth_login)):
    return project_service.get_projects_content(content_id=content_id, project_id=project_id)


@projects_router.post("/{project_id}/credits")
@standard_response
async def add_project_credit(project_id: int, credit: CreditCreate, user=Depends(auth_login)):
    return project_service.create_credit(credit=credit)
    # 实现添加项目学分认定的逻辑


@projects_router.post("/{project_id}/contents/{content_id}/submissions")
@standard_response
async def submit_project_content(project_id: int, content_id: int, submission: SubmissionCreate,
                                 user=Depends(auth_login)):
    # 可能需要增加对提交权限的处理
    return project_service.create_submission(submission=submission)
    # 实现提交项目要求内容的逻辑


@projects_router.post("/{project_id}/contents/{content_id}/scores")
@standard_response
async def score_project_content(project_id: int, content_id: int, score: ScoreCreate, user=Depends(auth_login)):
    return project_service.create_score(score=score)
    # 实现对项目内容打分的逻辑


@projects_router.get("/{project_id}/contents/{content_id}/submissions/{user_id}")
@standard_response
async def view_user_submission(project_id: int, content_id: int, user_id: int, viewer=Depends(auth_login)):
    return project_service.get_user_submission_list(project_id=project_id, content_id=content_id, user_id=user_id)
    # 实现查看用户在一个内容下的提交内容的逻辑


@projects_router.get("/{project_id}/members")
@standard_response
async def list_project_members(project_id: int, user=Depends(auth_login)):
    pass  # 实现查看参加项目的成员列表的逻辑


@projects_router.post("/{project_id}/contents/{content_id}/submit")
@standard_response
async def create_user_submission(project_id: int, content_id: int,
                                 User_submission: user_submission, user=Depends(auth_login)):
    return project_service.create_user_submission(uer_submission=User_submission)
    # 实现用户提交的逻辑
