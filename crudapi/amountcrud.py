from typing import Any, Type, List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from db.model import Amount
from Basemodel.financial_Basemodel import AmountAdd
from sqlalchemy import func, case


class AmountApi:
    def __init__(self, model: Type[Amount]):
        self.model = model
        # self.model = Api

    def save_amount(self, obj_in: AmountAdd, db: Session):
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Amount(**obj_dict)
        print(obj_dict)
        db.add(obj_add)
        db.commit()
        db.refresh(obj_add)
        return jsonable_encoder(obj_add)

    def query_total(self, Id: int, db: Session):
        result = db.query(func.sum(self.model.amount)).filter(self.model.finance_id == Id,
                                                              self.model.state == 0,
                                                              self.model.has_delete == 0).scalar()
        result2 = db.query(func.sum(self.model.amount)).filter(self.model.finance_id == Id,
                                                               self.model.state == 1,
                                                               self.model.has_delete == 0).scalar()
        if result is None:
            result = 0
        if result2 is None:
            result2 = 0
        return result - result2

    def query_amount(self, ID: int, pn: int, pg: int, db: Session):
        query = db.query(self.model).filter_by(finance_id=ID, has_delete=0)
        total_count = query.count()
        # 计算页数和查询偏移量
        total_pages = (total_count // pg) + (1 if total_count % pg > 0 else 0)
        offset = (pn - 1) * pg
        # 执行分页查询
        results = query.offset(offset).limit(pg).all()
        # 序列化结果
        serialized_results = []
        for result in results:
            serialized_result = {
                'state': result.state,
                'amount': result.amount,
                'oper_dt': result.oper_dt.timestamp()
            }
            serialized_results.append(serialized_result)
        # 构建结果字典
        result_dict = {
            'num': total_count,
            'pn': pn,
            'pg': pg,
            'total_pages': total_pages,
            'rows': serialized_results
        }
        return result_dict

    def delete_by_id(self, Id: int, db: Session):
        db.query(self.model).filter(self.model.Id == Id).update({"has_delete": 1})
        db.commit()
        return 0

    def delete_by_financial(self, Id: int, db: Session):
        db.query(self.model).filter(self.model.finance_id == Id).update({"has_delete": 1})
        db.commit()
        return 0

    def check_byId(self, Id: int, db: Session):
        query = db.query(self.model).filter_by(Id=Id, has_delete=0)
        total_count = query.count()
        return total_count

    def check_by_id(self, Id: int, db: Session):
        return db.query(self.model).filter(self.model.Id == Id, self.model.has_delete == 0).first()


api = AmountApi(Amount)
