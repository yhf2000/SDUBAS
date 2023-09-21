from pydantic import BaseModel, ConfigDict, field_serializer, Field
from typing import List, Optional
from datetime import datetime
from type.permissions import Add_Role_For_Work_Base, create_role_privilege_base
from utils.times import getMsTime


class ProjectContentBase(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    project_id: int = None
    type: int = Field(..., ge=0, le=2)
    name: str = Field(..., strip_whitespace=True, min_length=1)
    prefix: Optional[str] = None
    file_id: Optional[int] = None
    content: Optional[str] = None
    weight: float
    feature: Optional[str] = None
    has_delete: int = 0
    file_time: int = None


class ProjectContentBaseOpt(ProjectContentBase):
    id: int = None


class ProjectBase(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    name: str = Field(..., strip_whitespace=True, min_length=1)
    type: str = Field(..., strip_whitespace=True, min_length=1)
    tag: str = Field(..., strip_whitespace=True, min_length=1)
    img_id: int = Field(..., gt=0)
    active: int = Field(..., ge=0, le=2)
    create_dt: datetime = None
    has_delete: int = 0


class ProjectBase_Opt(ProjectBase):
    id: int

    @field_serializer('create_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class ProjectCreate(ProjectBase):
    contents: List[ProjectContentBase]
    roles: List[Add_Role_For_Work_Base]


class ProjectUpdate(BaseModel):
    name: str = Field(..., description="Name of the project", min_length=1, strip_whitespace=True)
    tag: str = Field(..., description="Tag of the project", min_length=1, strip_whitespace=True)
    active: int = Field(..., description="Status of the project (0-2)", ge=0, le=2)


class CreditCreate(BaseModel):
    project_id: int = Field(..., gt=0)
    role_id: int = Field(..., gt=0)
    credit: Optional[float] = None
    type: str = Field(..., description="Type of the projectContent", min_length=1, strip_whitespace=True)


class Credit_Opt(CreditCreate):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    id: int


class SubmissionCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    name: str = Field(..., description="Name of the project", min_length=1, strip_whitespace=True)
    pro_content_id: int = Field(..., gt=0)
    type: int = Field(..., ge=0, le=1)
    count_limit: Optional[int] = None
    size_limit: Optional[int] = None
    type_limit: Optional[str] = None


class SubmissionListCreate(BaseModel):
    addSubmissions: List[SubmissionCreate]


class Submission_Opt(SubmissionCreate):
    id: int


class ScoreCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    user_pcs_id: int = None
    judger: int = None
    user_id: int = Field(..., gt=0)
    honesty: str
    honesty_weight: float = None
    is_pass: int = Field(..., ge=-1, le=1)
    score: Optional[float] = None
    comment: str
    judge_dt: datetime = None
    viewed_time: int = None  # 视频文件检查次数，可空
    last_check_time: datetime = None  # 最新一次检查时间


class user_submission(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    pc_submit_id: int = Field(..., gt=0)
    user_id: int = None
    file_id: Optional[int] = None
    content: Optional[str] = None
    submit_dt: datetime = None


class user_submission_Opt(user_submission):
    id: int

    @field_serializer('submit_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class project_content_renew(BaseModel):
    contents: List[ProjectContentBaseOpt]


class content_score(ScoreCreate):
    id: int

    @field_serializer('judge_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class User_Opt(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    id: int
    username: str
    password: str
    email: str
    card_id: Optional[str]
    registration_dt: datetime
    storage_quota: int
    status: int
    has_delete: int

    @field_serializer('registration_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class video_finish_progress(BaseModel):
    content_id: int
