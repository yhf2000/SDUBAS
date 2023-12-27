import hashlib
from datetime import datetime, date
from typing import Any, Union
from pydantic import BaseModel, ConfigDict, Field


class login_interface(BaseModel):
    username: str = None
    password: str = None


class oj_login_interface(BaseModel):
    oj_username: str = None
    oj_password: str = None


class register_interface(login_interface):
    email: str = None


class captcha_interface(register_interface):
    captchaId: str = None
    captcha: str = None
    type: int = None


class user_add_interface(register_interface):
    card_id: str = None


class user_add_batch_interface(BaseModel):
    information_list: list
    role_id: int


class session_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    user_id: int
    file_id: int = None
    token: str
    use: int = 0
    token_s6: str = None
    use_limit: int = None
    exp_dt: int
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
    school_logo_id: int = None


class college_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    name: str = None
    school_id: int = None
    college_logo_id: int = None


class major_interface(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    name: str = None
    school_id: int = None
    college_id: int = None
    education_program: Union[dict, None] = None


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
    service_id: Union[int, None] = None
    operation_type: str
    func: str
    parameters: str
    oper_user_id: int
    oper_hash: str = None
    oper_dt: datetime

    def get_oper_hash(self):
        hash_object = hashlib.sha256()
        hash_object.update(self.func.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        return hash_hex


class user_info_interface(BaseModel):
    card_id: str = None
    user_id: int = None
    realname: str = None
    gender: int = None
    major_id: int = None
    class_id: int = None
    enrollment_dt: date = None
    graduation_dt: date = None


class admin_user_add_interface(user_add_interface, user_info_interface):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
    role_id: int
    school: int = None
    college: int = None
    confirm: str = None


class parameters_interface(BaseModel):
    url: str
    para: Any
    body: Any


class user_interface(BaseModel):
    username: str
    realname: str


class reason_interface(BaseModel):
    reason: str


class education_program_interface(BaseModel):
    major_id: int
    thought_political_theory: float = None
    college_sports: float = None
    college_english: float = None
    chinese_culture: float = None
    art_aesthetics: float = None
    innovation_entrepreneurship: float = None
    humanities: float = None
    social_sciences: float = None
    scientific_literacy: float = None
    information_technology: float = None
    general_education_elective: float = None
    major_compulsory_courses: float = None
    major_elective_courses: float = None
    key_improvement_courses: float = None
    qilu_entrepreneurship: float = None
    jixia_innovation: float = None
