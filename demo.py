import time
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer
from sqlalchemy import Column, Integer, VARCHAR, DateTime


from model.db import dbSession, Base
from utils.times import getMsTime




class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(64), index=True)
    created_at = Column(DateTime, index=True)


class IdModel(BaseModel):
    id: int


class UserModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )

    name: str
    created_at: datetime


class UserModelOpt(UserModel):
    @field_serializer('created_at')
    def serialize_dt(self, dt: datetime, _info):
        return getMsTime(dt)


class UserInfoModelOpt(UserModelOpt, IdModel):
    pass


if __name__ == "__main__":
    db = dbSession()
    user = UserModel(
        name="user_name0",
        created_at=datetime.now()
    )

    user_orm = User(**user.model_dump())
    db.add(user_orm)

    with db.get_db() as s:
        u = s.query(User).filter(User.id == 123).first()
        us = UserInfoModelOpt.model_validate(u)

        print(us.model_dump())
