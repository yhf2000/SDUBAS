from typing import Any, Optional
from fastapi.encoders import jsonable_encoder
from model.financial import Resource, Financial
from service.user import OperationModel
from type.financial import ResourceAdd, ApplyBody, Bill_basemodel, Financial_Basemodel, AmountAdd, FinancialAdd
from type.financial import Financial_ModelOpt, BillModelOpt, Resource_Basemodel
from model.financial import Bill
from model.db import dbSession
from type.page import dealDataList
from type.user import operation_interface
from utils.response import page
from fastapi import HTTPException
from sqlalchemy import func
from service.permissions import roleModel


def operation_commit(service_type: int, func: str, parameters: str, oper_user_id: int,
                     service_id: Optional[int] = None):
    if service_id is None:
        operation_commit = operation_interface(service_type=service_type,
                                               func=func, parameters=parameters, oper_user_id=oper_user_id)
    else:
        operation_commit = operation_interface(service_type=service_type, service_id=service_id,
                                               func=func, parameters=parameters, oper_user_id=oper_user_id)
    operation_service = OperationModel()
    operation_service.add_operation(obj=operation_commit)


class ResourceModel(dbSession):
    def save_resource(self, obj_in: ResourceAdd, user_id: int):  # 增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Resource(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            operation_commit(5, "添加资源", "用户添加资源", user_id, obj_add.Id)
            return obj_add.Id

    def delete(self, Id: int, user_id: int):  # 删除
        with self.get_db() as session:
            session.query(Resource).filter(Resource.Id == Id).update({"has_delete": 1})
            session.commit()
            operation_commit(5, "删除资源", "用户删除资源", user_id, Id)
            return Id

    def check_by_id(self, Id: int, user_id: int):  # 通过主键获取
        with self.get_db() as session:
            Resource_template = session.query(Resource).filter(Resource.Id == Id, Resource.has_delete == 0).first()
        if Resource_template is not None:
            Resource_dict = Resource_Basemodel.model_validate(Resource_template)
            operation_commit(5, "查询某一资源", "用户查询某一资源", user_id, Id)
            return Resource_dict.model_dump(exclude={'has_delete'})
        else:
            raise HTTPException(status_code=404, detail="Item not found")

    def get_resource_by_user(self, user: Any, pg: page, user_id: int):  # 获取当前用户所有可用资源
        with self.get_db() as session:
            role_model = roleModel()
            role_list = role_model.search_role_by_user(user)
            service_id = role_model.search_service_id(role_list, service_type=5, name="查看资源")
            query = session.query(Resource).filter(Resource.has_delete == 0, Resource.Id.in_(service_id))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            operation_commit(5, "查询资源列表", "用户查询资源列表", user_id)
            return total_count, dealDataList(data, Resource_Basemodel, {'has_delete'})

    def apply_resource(self, user: Any, Id: int, date: ApplyBody):
        # 权限查询相关的业务类型，业务Id,角色类型，查询模板角色id
        # 输入模板角色ID，与相关参数，添加接口
        # 返回成功或者失败
        return

    def count_Update(self, Id: int, count: int, user_id: int):  # 修改Note
        with self.get_db() as session:
            session.query(Resource).filter(Resource.Id == Id).update({"count": count})
            session.commit()
            operation_commit(5, "修改资源数量", "用户修改资源数量", user_id, Id)
            return Id

    def get_resource_apply_by_id(self, Id: int):  # 获取某项资源的所有申请
        # 权限查询相关的业务类型，业务Id,角色类型，查询模板角色id
        # 输入模板角色ID，查询所有非模板角色，的模板id为XXX的申请中的角色，与userid表格联合一下返回
        # 返回成功或者失败
        return

    def approve_apply_by_roleid(self, Id: int):
        # 直接修改角色id，修改为可用
        return

    def refuse_apply_by_roleid(self, Id: int):
        # 直接修改角色id，修改为不可用
        return


class BillModel(dbSession):
    def save_amount(self, obj_in: AmountAdd, user_id: int):  # 增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Bill(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            operation_commit(6, "添加资金收支", "用户添加资金收支", user_id, obj_in.finance_id)
            return jsonable_encoder(obj_add.Id)

    def query_total(self, Id: int, user_id: int):  # 查询全部金额
        with self.get_db() as session:
            # 查询收入，未删除的和
            result = session.query(func.sum(Bill.amount)).filter(Bill.finance_id == Id,
                                                                 Bill.state == 0,
                                                                 Bill.has_delete == 0).scalar()
            # 查询支出，未删除的和
            result2 = session.query(func.sum(Bill.amount)).filter(Bill.finance_id == Id,
                                                                  Bill.state == 1,
                                                                  Bill.has_delete == 0).scalar()
        # 收入或支出没有赋值0
        if result is None:
            result = 0
        if result2 is None:
            result2 = 0
        operation_commit(6, "查询资金总额", "用户查询资金总额", user_id, Id)
        return result - result2

    def query_amount(self, ID: int, pg: page, user_id: int):  # 查询分页流水
        with self.get_db() as session:
            query = session.query(Bill).filter_by(finance_id=ID, has_delete=0)
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            # 序列化结
            operation_commit(6, "查询资金流水", "用户查询资金流水", user_id, ID)
            return total_count, dealDataList(data, BillModelOpt, {'has_delete'})

    def delete_by_id(self, Id: int, user_id: int, financial_id: int):
        with self.get_db() as session:
            session.query(Bill).filter(Bill.Id == Id).update({"has_delete": 1})
            session.commit()
            operation_commit(6, "删除资金某一流水", "用户删除资金流水", user_id, financial_id)
            return Id

    def delete_by_financial(self, Id: int, user_id: int):  # 通过外键删除
        with self.get_db() as session:
            session.query(Bill).filter(Bill.finance_id == Id).update({"has_delete": 1})
            session.commit()
            operation_commit(6, "删除资金全部流水", "用户删除资金流水", user_id, Id)
            return Id

    def check_by_id(self, Id: int, user_id: int):  # 通过主键获取
        with self.get_db() as session:
            return session.query(Bill).filter(Bill.Id == Id, Bill.has_delete == 0).first()


class FinancialModel(dbSession):
    def save_financial(self, obj_in: FinancialAdd, user_id: int):  # 增加
        obj_dict = jsonable_encoder(obj_in)
        obj_add = Financial(**obj_dict)
        with self.get_db() as session:
            session.add(obj_add)
            session.flush()
            session.commit()
            operation_commit(6, "添加资金", "用户添加资金", user_id, obj_add.Id)
            return obj_add.Id

    def check_by_id(self, Id: int, user_id: int):  # 获取，通过主键
        with self.get_db() as session:
            Financial_list = session.query(Financial).filter(Financial.Id == Id, Financial.has_delete == 0).first()
        if Financial_list is None:
            raise HTTPException(status_code=404, detail="Item not found")
        Financial_list3 = Financial_ModelOpt.model_validate(Financial_list)
        operation_commit(6, "查询某一资金", "用户查询资金", user_id, Id)
        return Financial_list3.model_dump(exclude={'has_delete'})

    def delete(self, Id: int, user_id: int):  # 删除，通过主键
        with self.get_db() as session:
            session.query(Financial).filter(Financial.Id == Id).update({"has_delete": 1})
            session.commit()
            operation_commit(6, "删除资金", "用户删除资金", user_id, Id)
            return Id

    def note_Update(self, Id: int, note: str, user_id: int):  # 修改Note
        with self.get_db() as session:
            session.query(Financial).filter(Financial.Id == Id).update({"note": note})
            session.commit()
            operation_commit(6, "修改资金note", "用户修改资金note", user_id, Id)
            return Id

    def get_financial_by_user(self, user: Any, pg: page, user_id: int):  # 获取当前用户所有可用资金
        with self.get_db() as session:
            role_model = roleModel()
            role_list = role_model.search_role_by_user(user)
            service_id = role_model.search_service_id(role_list, service_type=6, name="查看资金")
            query = session.query(Financial).filter(Financial.has_delete == 0, Financial.Id.in_(service_id))
            total_count = query.count()  # 总共
            # 执行分页查询
            data = query.offset(pg.offset()).limit(pg.limit())  # .all()
            operation_commit(6, "查询资金列表", "用户查询资金列表", user_id)
            return total_count, dealDataList(data, Financial_ModelOpt, {'has_delete'})
