from typing import Any, Type, List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from db.model import Financial
from Basemodel.financial_Basemodel import FinancialAdd


class FinancialApi:
    def __init__(self, model: Type[Financial]):
        self.model = model
        # self.model = Api

    def save_financial(self, obj_in: FinancialAdd, db: Session):
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Financial(**obj_dict)
        db.add(obj_add)
        db.commit()
        db.refresh(obj_add)
        return jsonable_encoder(obj_add)

    def check_by_id(self, Id: int, db: Session):
        return db.query(self.model).filter(self.model.Id == Id, self.model.has_delete == 0).first()

    def delete(self, Id: int, db: Session):
        db.query(self.model).filter(self.model.Id == Id).update({"has_delete": 1})
        db.commit()
        return 0


api = FinancialApi(Financial)
