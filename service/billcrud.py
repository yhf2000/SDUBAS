from typing import Any, Type, List
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from db.model import Bill, dbSession
from model.financial_Basemodel import AmountAdd
from sqlalchemy import func, case
from model.financial_Basemodel import page


class BillModel(dbSession):
    def save_amount(self, obj_in: AmountAdd):#增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Bill(**obj_dict)
        self.session.add(obj_add)
        self.session.flush()
        self.session.commit()
        return jsonable_encoder(obj_add.Id)

    def query_total(self, Id: int):#查询全部金额
        #查询收入，未删除的和
        result = self.session.query(func.sum(Bill.amount)).filter(Bill.finance_id == Id,
                                                                  Bill.state == 0,
                                                                  Bill.has_delete == 0).scalar()
        #查询支出，未删除的和
        result2 = self.session.query(func.sum(Bill.amount)).filter(Bill.finance_id == Id,
                                                                   Bill.state == 1,
                                                                   Bill.has_delete == 0).scalar()
        #收入或支出没有赋值0
        if result is None:
            result = 0
        if result2 is None:
            result2 = 0
        return result - result2

    def query_amount(self, ID: int, pg: page):#查询分页流水
        query = self.session.query(Bill).filter_by(finance_id=ID, has_delete=0)
        total_count = query.count()#总共
        # 执行分页查询
        data = query.offset(pg.offset()).limit(pg.limit())  # .all()
        # 序列化结
        return total_count, self.dealDataList(data, ['oper_dt'], ['financial_id', 'has_delete'])

    def delete_by_id(self, Id: int):
        self.session.query(Bill).filter(Bill.Id == Id).update({"has_delete": 1})
        self.session.commit()
        return Id

    def delete_by_financial(self, Id: int):#通过外键删除
        self.session.query(Bill).filter(Bill.finance_id == Id).update({"has_delete": 1})
        self.session.commit()
        return Id

    def check_by_id(self, Id: int):#通过主键获取
        return self.session.query(Bill).filter(Bill.Id == Id, Bill.has_delete == 0).first()
