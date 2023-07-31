from typing import Any, Type, List

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from model.financial_dbmodel import Financial, dbSession
from model.financial_Basemodel import FinancialAdd, Financial_Basemodel
from type.page import page, convert_result_to_model


class FinancialModel(dbSession):
    def save_financial(self, obj_in: FinancialAdd):  # 增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Financial(**obj_dict)
        self.session.add(obj_add)
        self.session.flush()
        self.session.commit()
        return obj_add.Id

    def check_by_id(self, Id: int):  # 获取，通过主键
        Financial_list = self.session.query(Financial).filter(Financial.Id == Id, Financial.has_delete == 0).first()
        Financial_list3 = convert_result_to_model(Financial_list, Financial_Basemodel)
        if Financial_list is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return Financial_list3.model_dump(exclude={'has_delete'})

    def delete(self, Id: int):  # 删除，通过主键
        self.session.query(Financial).filter(Financial.Id == Id).update({"has_delete": 1})
        self.session.commit()
        return Id

    def note_Update(self, Id: int, note: str):  # 修改Note
        self.session.query(Financial).filter(Financial.Id == Id).update({"note": note})
        self.session.commit()
        return Id

    def get_financial_by_user(self, user: Any, pg: page):  # 获取当前用户所有可用资金
        # query=调用权限函数   返回一个query,可用
        # 分页相关 result=query.offset(offset).limit(pg)  使用直接获取
        # 整理函数  返回结果
        return
