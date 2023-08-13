from pydantic import BaseModel, ConfigDict, field_serializer, Field
from typing import List, Optional
from datetime import datetime

from utils.times import getMsTime


class ProjectContentBase(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    project_id: int = None
    type: int
    fa_id: Optional[int] = None
    name: str
    file_id: Optional[int] = None
    content: Optional[str] = None
    weight: float
    feature: Optional[str] = None


class ProjectContentBaseOpt(ProjectContentBase):
    id: int


class ProjectBase(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    name: str
    type: str
    tag: str
    img_id: int
    active: int
    create_dt: datetime = None
    has_delete: int = 0


class ProjectBase_Opt(ProjectBase):
    id: int

    @field_serializer('create_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class ProjectCreate(ProjectBase):
    contents: List[ProjectContentBase]


class ProjectUpdate(BaseModel):
    name: str = Field(..., description="Name of the project", min_length=1, strip_whitespace=True)
    tag: str = Field(..., description="Tag of the project", min_length=1, strip_whitespace=True)
    active: int = Field(..., description="Status of the project (0-2)", ge=0, le=2)


class CreditCreate(BaseModel):
    project_id: int
    role_id: int
    credit: Optional[float] = None


class SubmissionCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    pro_content_id: int
    type: int
    count_limit: Optional[int] = None
    size_limit: Optional[int] = None
    type_limit: Optional[str] = None


class Submission_Opt(SubmissionCreate):
    id: int


class ScoreCreate(BaseModel):
    user_pcs_id: int
    judger: int
    user_id: int
    honesty: str
    honesty_weight: float
    is_pass: int
    score: Optional[float] = None
    comment: str
    judge_dt: datetime = None


class user_submission(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    pc_submit_id: int
    user_id: int
    file_id: Optional[int]
    content: Optional[str]
    submit_dt: datetime = None


class user_submission_Opt(user_submission):
    id: int

    @field_serializer('submit_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)
