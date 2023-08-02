import hashlib
import random
from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, field_serializer

from utils.times import getMsTime


class user_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
    id: int = None
    username: str
    password: str
    email: str
    card_id: str
    registration_dt: datetime
    storage_quota: str
    status: str
    has_delete: int



class user_interface_Opt(user_interface):
    @field_serializer('registration_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class login_interface(BaseModel):
    username: str
    password: str


class register_interface(login_interface):
    email: str


class session_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    user_id: int
    file_id: int = None
    token: str
    token_s6: str = None
    use: int = 0
    use_limit: int = None
    exp_dt: datetime
    ip: str
    user_agent: str
    func_type: int


class session_interface_Opt(session_interface):
    @field_serializer('exp_dt')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class school_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    name: str = None
    school_abbreviation: str = None


class college_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    name: str = None
    school_id: int = None


class major_interface(college_interface):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    college_id: int = None


class class_interface(college_interface):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    college_id: int = None


class user_info_interface(BaseModel):
    card_id: str = None
    user_id: int = None
    realname: str
    gender: str
    major_id: str
    class_id: str
    enrollment_dt: date
    graduation_dt: date


class user_info_interface_Opt(user_info_interface):
    @field_serializer('enrollment_dt')
    @field_serializer('graduation_dt')
    def serialize_dt(self, dt: date, _info):
        return getMsTime(dt)


class nothing(BaseModel):
    email: str = None
    token_s6: str = None


def MD5(password):  # MD5对密码加密
    m = hashlib.md5()
    m.update(password.encode("utf8"))
    return m.hexdigest()


def get_email_token():  # 生成email的验证码
    email_token = ''
    for i in range(8):
        email_token += str(random.randint(0, 9))  # 生成八位随机验证码
    return email_token
