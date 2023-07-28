from typing import Any, Type, List
from fastapi.encoders import jsonable_encoder
from db.model import Resource
from model.financial_Basemodel import ResourceAdd
from db.model import dbSession


class ResourceModel(dbSession):
    def save_resource(self, obj_in: ResourceAdd):#增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Resource(**obj_dict)
        self.session.add(obj_add)
        self.session.flush()
        self.session.commit()
        return obj_add.Id

    def delete(self, Id: int):#删除
        self.session.query(Resource).filter(Resource.Id == Id).update({"has_delete": 1})
        self.session.commit()
        return Id

    def check_by_id(self, Id: int):#通过主键获取
        return self.session.query(Resource).filter(Resource.Id == Id, Resource.has_delete == 0).first()


