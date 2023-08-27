import hashlib
import json
from datetime import datetime, date

from pydantic import BaseModel, ConfigDict
from typing import Any
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
    service_id: int = None
    func: str
    parameters: str
    oper_user_id: int
    oper_hash: str = None

    def get_oper_hash(self):
        hash_object = hashlib.sha256()
        hash_object.update(self.parameters.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        return hash_hex


class user_info_interface(BaseModel):
    card_id: str = None
    user_id: int = None
    realname: str = None
    gender: str = None
    major_id: str = None
    class_id: str = None
    enrollment_dt: date = None
    graduation_dt: date = None


class admin_user_add_interface(user_add_interface, user_info_interface):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )


class parameters_interface(BaseModel):
    url: str
    para: Any
    body: Any
