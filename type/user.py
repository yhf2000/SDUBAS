import hashlib
import json
from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, field_serializer

from utils.times import getMsTime


class login_interface(BaseModel):
    username: str = None
    password: str = None


class register_interface(login_interface):
    email: str = None
    type: int = None
    registration_dt: datetime = datetime.now()


class captcha_interface(register_interface):
    captchaId: str = None
    captcha: str = None
    type: int = None


class user_add_interface(register_interface):
    card_id: str = None


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


class password_interface(BaseModel):
    new_password: str = None
    old_password: str = None


class email_interface(register_interface):
    token_s6: str = None
    card_id: str = None
    type: int = 0


class operation_interface(BaseModel):
    service_type: int
    service_id: int
    func: str
    parameters: str
    oper_user_id: int
    oper_hash: str = None

    def get_oper_hash(self):
        operation_json = json.dumps(operation_interface.model_dump(self))
        sha256_hash = hashlib.sha256(operation_json.encode()).hexdigest()
        return sha256_hash


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


class admin_user_add_interface(user_add_interface, user_info_interface):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
