from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProjectContentBase(BaseModel):
    project_id: int
    type: int
    fa_id: Optional[int] = None
    name: str
    file_id: Optional[int] = None
    content: Optional[str] = None
    weight: float
    feature: Optional[str] = None


class ProjectBase(BaseModel):
    name: str
    type: str
    tag: str
    img_id: int
    active: int
    create_dt: datetime
    has_delete: int


class ProjectCreate(ProjectBase):
    contents: List[ProjectContentBase]


class ProjectUpdate(ProjectBase):
    id: int


class CreditCreate(BaseModel):
    project_id: int
    role_id: int
    credit: Optional[float] = None


class SubmissionCreate(BaseModel):
    pro_content_id: int
    type: int
    count_limit: Optional[int] = None
    size_limit: Optional[int] = None
    type_limit: Optional[str] = None


class ScoreCreate(BaseModel):
    user_pcs_id: int
    user_id: int
    honesty: str
    honesty_weight: float
    is_pass: int
    score: Optional[float] = None
    comment: str
    judge_dt: datetime


