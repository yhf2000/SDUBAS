from fastapi import APIRouter, Depends

from service.project import ProjectService
from type.project import CreditCreate, SubmissionCreate, ScoreCreate, ProjectUpdate, ProjectCreate
from utils.auth_login import auth_login
from utils.response import standard_response

projects_router = APIRouter()

project_service = ProjectService()


@projects_router.post("/")
@standard_response
async def create_project(project: ProjectCreate, user=Depends(auth_login)) -> Project:
    return project_service.create_project(project)


@projects_router.put("/{project_id}")
@standard_response
async def update_project(project_id: int, project: ProjectUpdate, user=Depends(auth_login)):
    pass  # 实现编辑项目的逻辑


@projects_router.delete("/{project_id}")
@standard_response
async def delete_project(project_id: int, user=Depends(auth_login)):
    pass  # 实现删除项目的逻辑


@projects_router.get("/")
@standard_response
async def list_projects(user=Depends(auth_login)):
    pass  # 实现查询项目列表的逻辑


@projects_router.get("/{project_id}")
@standard_response
async def get_project(project_id: int, user=Depends(auth_login)):
    pass  # 实现查询项目详情的逻辑


@projects_router.get("/{project_id}/contents")
@standard_response
async def get_project_content(project_id: int, user=Depends(auth_login)):
    pass  # 实现查询项目内容结构表的逻辑


@projects_router.get("/{project_id}/contents/{content_id}")
@standard_response
async def get_specific_project_content(project_id: int, content_id: int, user=Depends(auth_login)):
    pass  # 实现查询具体项目内容的逻辑


@projects_router.post("/{project_id}/credits")
@standard_response
async def add_project_credit(project_id: int, credit: CreditCreate, user=Depends(auth_login)):
    pass  # 实现添加项目学分认定的逻辑


@projects_router.post("/{project_id}/contents/{content_id}/submissions")
@standard_response
async def submit_project_content(project_id: int, content_id: int, submission: SubmissionCreate,
                                 user=Depends(auth_login)):
    pass  # 实现提交项目要求内容的逻辑


@projects_router.post("/{project_id}/contents/{content_id}/scores")
@standard_response
async def score_project_content(project_id: int, content_id: int, score: ScoreCreate, user=Depends(auth_login)):
    pass  # 实现对项目内容打分的逻辑


@projects_router.get("/{project_id}/contents/{content_id}/submissions/{user_id}")
@standard_response
async def view_user_submission(project_id: int, content_id: int, user_id: int, viewer=Depends(auth_login)):
    pass  # 实现查看用户在一个内容下的提交内容的逻辑


@projects_router.get("/{project_id}/members")
@standard_response
async def list_project_members(project_id: int, user=Depends(auth_login)):
    pass  # 实现查看参加项目的成员列表的逻辑
