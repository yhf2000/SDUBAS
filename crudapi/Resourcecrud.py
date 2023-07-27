from typing import Any, Type, List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from db.model import Resource
from Basemodel.financial_Basemodel import ResourceAdd


class ResourceApi:
    def __init__(self, model: Type[Resource]):
        self.model = model
        # self.model = Api

    def save_resource(self, obj_in: ResourceAdd, db: Session):
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Resource(**obj_dict)
        db.add(obj_add)
        db.commit()
        db.refresh(obj_add)
        return jsonable_encoder(obj_add)

    def delete(self, Id: int, db: Session):
        db.query(self.model).filter(self.model.Id == Id).update({"has_delete": 1})
        db.commit()
        return 0

    def check_by_id(self, Id: int, db: Session):
        return db.query(self.model).filter(self.model.Id == Id, self.model.has_delete == 0).first()


api = ResourceApi(Resource)
